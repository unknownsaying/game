// division_fractal_topology.cpp
// C++17 – Build a Sierpiński carpet fractal and a corresponding expanding adjacency graph

#include <algorithm>
#include <array>
#include <cmath>
#include <future>
#include <iostream>
#include <list>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// ----------------------------------------------------------------------
// 2‑D point and rectangle helper
// ----------------------------------------------------------------------
struct Point {
    double x, y;
    Point(double x = 0, double y = 0) : x(x), y(y) {}
};

struct Rectangle {
    double xmin, ymin, xmax, ymax;
    Rectangle(double x0, double y0, double x1, double y1)
        : xmin(x0), ymin(y0), xmax(x1), ymax(y1) {}

    double width()  const { return xmax - xmin; }
    double height() const { return ymax - ymin; }

    // Subdivide into 3×3 sub‑rectangles, returning only the 8 kept (centre omitted)
    std::vector<Rectangle> subdivide() const {
        double w = width() / 3.0;
        double h = height() / 3.0;
        std::vector<Rectangle> rects;
        rects.reserve(8);
        for (int iy = 0; iy < 3; ++iy) {
            for (int ix = 0; ix < 3; ++ix) {
                if (ix == 1 && iy == 1) continue;   // discard centre
                rects.emplace_back(
                    xmin + ix * w, ymin + iy * h,
                    xmin + (ix+1) * w, ymin + (iy+1) * h
                );
            }
        }
        return rects;
    }

    // Determine directional neighbour: returns true if neighbourRect exists (axis‑aligned adjacency)
    // direction: 0=left, 1=right, 2=bottom, 3=top
    bool adjacent(const Rectangle& other, int direction) const {
        constexpr double eps = 1e-9;
        switch (direction) {
            case 0: // left
                return std::abs(xmax - other.xmin) < eps &&
                       ymin < other.ymax - eps && ymax > other.ymin + eps;
            case 1: // right
                return std::abs(xmin - other.xmax) < eps &&
                       ymin < other.ymax - eps && ymax > other.ymin + eps;
            case 2: // bottom
                return std::abs(ymax - other.ymin) < eps &&
                       xmin < other.xmax - eps && xmax > other.xmin + eps;
            case 3: // top
                return std::abs(ymin - other.ymax) < eps &&
                       xmin < other.xmax - eps && xmax > other.xmin + eps;
        }
        return false;
    }
};

// ----------------------------------------------------------------------
// Forward declarations
// ----------------------------------------------------------------------
class TopologyGraph;

// ----------------------------------------------------------------------
// Cell: represents one occupied square in the fractal hierarchy
// ----------------------------------------------------------------------
class Cell : public std::enable_shared_from_this<Cell> {
public:
    using Ptr = std::shared_ptr<Cell>;
    using WeakPtr = std::weak_ptr<Cell>;

    int id;                     // unique node id in the topology graph
    Rectangle rect;             // geometric region
    int depth;                  // subdivision level (0 = root)
    bool subdivided;            // true if this cell has been replaced by children
    std::vector<Ptr> children;  // 8 children after subdivision, empty if not subdivided

    // Neighbour lists (indices correspond to direction 0..3)
    std::array<std::vector<Ptr>, 4> neighbours;

    Cell(int id, const Rectangle& r, int depth = 0)
        : id(id), rect(r), depth(depth), subdivided(false) {}

    // Subdivide this cell, returning newly created children
    std::vector<Ptr> subdivideCells(int& nextId) {
        if (subdivided) return children;   // already done

        std::vector<Rectangle> subRects = rect.subdivide();
        children.reserve(8);
        for (auto& subRect : subRects) {
            children.push_back(std::make_shared<Cell>(nextId++, subRect, depth + 1));
        }
        subdivided = true;
        return children;
    }
};

// ----------------------------------------------------------------------
// TopologyGraph: owns all cells (nodes) and handles edge expansion
// ----------------------------------------------------------------------
class TopologyGraph {
public:
    using CellPtr = Cell::Ptr;
    using CellWeakPtr = Cell::WeakPtr;

    std::unordered_map<int, CellPtr> nodes;     // map: id -> cell pointer
    int nextId = 0;

    // Mutex for thread‑safe subdivision of multiple root cells
    std::mutex mutex;

    // Add a root cell (must be called before subdivision)
    CellPtr addRoot(const Rectangle& rect) {
        auto cell = std::make_shared<Cell>(nextId++, rect, 0);
        nodes[cell->id] = cell;
        return cell;
    }

    // Build initial neighbour relations for a set of root cells (if more than one)
    void buildInitialNeighbours() {
        // Brute force: O(n²) for small n (roots are few)
        std::vector<CellPtr> all;
        for (auto& [id, cell] : nodes) all.push_back(cell);
        for (auto& a : all) {
            for (auto& b : all) {
                if (a->id == b->id) continue;
                for (int dir = 0; dir < 4; ++dir) {
                    if (a->rect.adjacent(b->rect, dir)) {
                        a->neighbours[dir].push_back(b);
                    }
                }
            }
        }
    }

    // Replace a cell with its children, rewriting edges in the graph.
    // This is the core topology expansion step.
    void expandCell(CellPtr cell) {
        if (!cell || cell->subdivided) return;

        // 1. Subdivide geometry and create children
        int dummyNextId = nextId;   // we will update nextId afterwards
        auto children = cell->subdivideCells(dummyNextId);
        // Now register children in the node map and update nextId
        for (auto& ch : children) {
            ch->id = nextId++;
            nodes[ch->id] = ch;
        }

        // 2. Transfer original neighbours to the appropriate boundary children.
        //    For each side, find which children touch that side and inherit that neighbour.
        const auto& origNeigh = cell->neighbours;
        for (int dir = 0; dir < 4; ++dir) {
            for (auto& neigh : origNeigh[dir]) {
                // For each neighbour, assign it to the child that is adjacent in that direction.
                for (auto& ch : children) {
                    if (ch->rect.adjacent(neigh->rect, dir)) {
                        // Add neighbour to child (both directions)
                        ch->neighbours[dir].push_back(neigh);
                        // Also inform the neighbour that this child is a neighbour on the opposite side
                        int oppDir = (dir + 2) % 4; // left<->right, top<->bottom
                        auto it = std::find(neigh->neighbours[oppDir].begin(),
                                            neigh->neighbours[oppDir].end(), cell);
                        if (it != neigh->neighbours[oppDir].end()) {
                            *it = ch;   // replace original cell with child
                        } else {
                            neigh->neighbours[oppDir].push_back(ch);
                        }
                    }
                }
            }
        }

        // 3. Remove the original cell from the node map.
        nodes.erase(cell->id);

        // 4. Build internal edges between the new children (they are adjacent to each other).
        for (size_t i = 0; i < children.size(); ++i) {
            for (size_t j = i+1; j < children.size(); ++j) {
                for (int dir = 0; dir < 4; ++dir) {
                    if (children[i]->rect.adjacent(children[j]->rect, dir)) {
                        children[i]->neighbours[dir].push_back(children[j]);
                        int oppDir = (dir + 2) % 4;
                        children[j]->neighbours[oppDir].push_back(children[i]);
                        // A single direction of adjacency is enough (avoid double counting)
                        break;
                    }
                }
            }
        }
    }
};

// ----------------------------------------------------------------------
// Recursive subdivision worker (can be called concurrently)
// ----------------------------------------------------------------------
void subdivideRecursive(TopologyGraph& graph, Cell::Ptr cell, int maxDepth) {
    if (!cell || cell->depth >= maxDepth) return;
    graph.expandCell(cell);

    // Launch tasks for children in parallel
    std::vector<std::future<void>> futures;
    for (auto& child : cell->children) {
        futures.push_back(std::async(std::launch::async,
            [&graph, child, maxDepth]() {
                subdivideRecursive(graph, child, maxDepth);
            }));
    }
    for (auto& f : futures) f.get();
}

// ----------------------------------------------------------------------
// Utility: ASCII art of the fractal using a bitmap approach
// ----------------------------------------------------------------------
std::string renderFractal(const TopologyGraph& graph, int resolution = 81) {
    // resolution must be odd for symmetry (e.g., 81 = 3^4)
    std::vector<char> pixels(resolution * resolution, ' ');
    for (const auto& [id, cell] : graph.nodes) {
        if (cell->subdivided) continue;   // only leaf cells matter
        // Map [0,1] to [0, resolution)
        auto x2pix = [resolution](double v) { return std::clamp(static_cast<int>(v * resolution + 0.5), 0, resolution-1); };
        int ix0 = x2pix(cell->rect.xmin);
        int ix1 = x2pix(cell->rect.xmax);
        int iy0 = x2pix(cell->rect.ymin);
        int iy1 = x2pix(cell->rect.ymax);
        for (int y = iy0; y < iy1; ++y)
            for (int x = ix0; x < ix1; ++x)
                pixels[y * resolution + x] = '#';
    }

    std::ostringstream oss;
    for (int y = resolution-1; y >= 0; --y) {
        for (int x = 0; x < resolution; ++x) {
            oss << pixels[y * resolution + x];
        }
        oss << '\n';
    }
    return oss.str();
}

// ----------------------------------------------------------------------
// Demo: build a 2‑level Sierpiński carpet, print fractal and adjacency
// ----------------------------------------------------------------------
int main() {
    TopologyGraph graph;

    // Define the initial unit square as the root cell
    auto root = graph.addRoot(Rectangle(0.0, 0.0, 1.0, 1.0));
    // If we had multiple root cells, we'd call buildInitialNeighbours() here,
    // but for a single square there are no external neighbours initially.

    // Perform fractal subdivision up to depth 3 (creates 8^3 = 512 cells)
    const int MAX_DEPTH = 3;
    subdivideRecursive(graph, root, MAX_DEPTH);

    // Print the fractal as ASCII
    std::cout << "Sierpiński Carpet (depth " << MAX_DEPTH << "):\n";
    std::cout << renderFractal(graph, 27) << std::endl;   // 27 = 3^3

    // Print the expanding topology (graph)
    std::cout << "Graph adjacency (leaf cells only):\n";
    for (const auto& [id, cell] : graph.nodes) {
        if (cell->subdivided) continue;   // only leaf cells
        std::cout << "Node " << id << " (rect [" 
                  << cell->rect.xmin << "," << cell->rect.ymin << "]-["
                  << cell->rect.xmax << "," << cell->rect.ymax << "]):\n";
        for (int dir = 0; dir < 4; ++dir) {
            const char* dirName[] = {"LEFT", "RIGHT", "BOTTOM", "TOP"};
            std::cout << "  " << dirName[dir] << ": ";
            for (auto& neigh : cell->neighbours[dir]) {
                std::cout << neigh->id << " ";
            }
            std::cout << "\n";
        }
    }

    std::cout << "Total leaf nodes: " << std::count_if(graph.nodes.begin(), graph.nodes.end(),
        [](auto& p) { return !p.second->subdivided; }) << std::endl;

    return 0;
}