// fractal_enum_topology.cpp
// C++20 – Fractal generation & topology expansion controlled by enums

#include <algorithm>
#include <array>
#include <cmath>
#include <execution>
#include <format>
#include <future>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <ranges>
#include <set>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <vector>

// ============================================================================
// Enums for fractal type and topology expansion rules
// ============================================================================
enum class FractalType {
    SierpinskiCarpet,   // 3x3 grid, remove centre
    VicsekCross,        // 3x3 grid, keep only center and edges
    CantorDust          // 2x2 grid, remove one diagonal
};

enum class TopologyExpansion {
    Standard,           // simple neighbour transfer to boundary children
    EdgePreserving      // guarantee that the adjacency graph remains planar
};

// Static information about each fractal
constexpr size_t subdivision_count(FractalType ft) {
    switch (ft) {
        case FractalType::SierpinskiCarpet: return 8;
        case FractalType::VicsekCross:      return 5;
        case FractalType::CantorDust:       return 3;
    }
    return 0;
}

constexpr std::string_view fractal_name(FractalType ft) {
    switch (ft) {
        case FractalType::SierpinskiCarpet: return "Sierpinski Carpet";
        case FractalType::VicsekCross:      return "Vicsek Cross";
        case FractalType::CantorDust:       return "Cantor Dust";
    }
    return "";
}

constexpr std::string_view expansion_name(TopologyExpansion exp) {
    switch (exp) {
        case TopologyExpansion::Standard:       return "Standard";
        case TopologyExpansion::EdgePreserving: return "Edge-Preserving";
    }
    return "";
}

// ============================================================================
// Point & Rectangle geometry
// ============================================================================
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

    // Subdivide according to the fractal type
    std::vector<Rectangle> subdivide(FractalType ft) const {
        double w = width() / 3.0;
        double h = height() / 3.0;
        std::vector<Rectangle> result;
        switch (ft) {
            case FractalType::SierpinskiCarpet:
                for (int iy = 0; iy < 3; ++iy)
                    for (int ix = 0; ix < 3; ++ix) {
                        if (ix == 1 && iy == 1) continue;
                        result.emplace_back(xmin + ix * w, ymin + iy * h,
                                            xmin + (ix+1) * w, ymin + (iy+1) * h);
                    }
                break;
            case FractalType::VicsekCross:
                // Keep center and the four edge midpoints
                for (int iy = 0; iy < 3; ++iy)
                    for (int ix = 0; ix < 3; ++ix) {
                        if ((ix == 1 && iy == 1) ||           // center
                            (ix == 1 && (iy == 0 || iy == 2)) || // top/bottom middle
                            (iy == 1 && (ix == 0 || ix == 2)))   // left/right middle
                            result.emplace_back(xmin + ix * w, ymin + iy * h,
                                                xmin + (ix+1) * w, ymin + (iy+1) * h);
                    }
                break;
            case FractalType::CantorDust:
                // Divide 2x2, keep three sub‑squares (omit top‑right)
                w = width() / 2.0;
                h = height() / 2.0;
                for (int iy = 0; iy < 2; ++iy)
                    for (int ix = 0; ix < 2; ++ix) {
                        if (ix == 1 && iy == 1) continue;
                        result.emplace_back(xmin + ix * w, ymin + iy * h,
                                            xmin + (ix+1) * w, ymin + (iy+1) * h);
                    }
                break;
        }
        return result;
    }

    // Directional adjacency (0:left,1:right,2:bottom,3:top)
    bool adjacent(const Rectangle& other, int dir) const {
        constexpr double eps = 1e-9;
        switch (dir) {
            case 0: return std::abs(xmax - other.xmin) < eps &&
                           ymin < other.ymax - eps && ymax > other.ymin + eps;
            case 1: return std::abs(xmin - other.xmax) < eps &&
                           ymin < other.ymax - eps && ymax > other.ymin + eps;
            case 2: return std::abs(ymax - other.ymin) < eps &&
                           xmin < other.xmax - eps && xmax > other.xmin + eps;
            case 3: return std::abs(ymin - other.ymax) < eps &&
                           xmin < other.xmax - eps && xmax > other.xmin + eps;
        }
        return false;
    }

    // Comparison for set
    bool operator<(const Rectangle& other) const {
        return std::tie(xmin, ymin, xmax, ymax) < std::tie(other.xmin, other.ymin, other.xmax, other.ymax);
    }
    bool operator==(const Rectangle& other) const = default;
};

// ============================================================================
// Topology: set of open sets = all unions of a given collection of sets (basis)
// ============================================================================
template<typename SetElement>
class Topology {
public:
    using BasisElement = SetElement;
    using OpenSet = std::set<BasisElement>;

    // Build from a basis (e.g., leaf cells)
    explicit Topology(const std::set<BasisElement>& basis) : basis_(basis) {
        generateAllUnions();
    }

    // Check if a set is open
    bool isOpen(const std::set<BasisElement>& subset) const {
        return openSets_.count(subset) > 0;
    }

    const std::set<OpenSet>& openSets() const { return openSets_; }
    size_t size() const { return openSets_.size(); }

private:
    std::set<BasisElement> basis_;
    std::set<OpenSet> openSets_;

    void generateAllUnions() {
        // Generate all unions of basis elements using iterative bitmask approach
        std::vector<BasisElement> basisVec(basis_.begin(), basis_.end());
        size_t n = basisVec.size();
        size_t total = 1ULL << n;   // 2^n subsets
        for (size_t mask = 0; mask < total; ++mask) {
            OpenSet s;
            for (size_t i = 0; i < n; ++i)
                if (mask & (1ULL << i))
                    s.insert(basisVec[i]);
            openSets_.insert(s);
        }
    }
};

// ============================================================================
// Cell – a node in the expanding topology graph
// ============================================================================
class Cell : public std::enable_shared_from_this<Cell> {
public:
    using Ptr = std::shared_ptr<Cell>;
    using WeakPtr = std::weak_ptr<Cell>;

    int id;
    Rectangle rect;
    int depth;
    bool subdivided = false;
    std::vector<Ptr> children;
    std::array<std::vector<Ptr>, 4> neighbours;   // directional

    Cell(int id, const Rectangle& r, int depth = 0) : id(id), rect(r), depth(depth) {}

    // Subdivide and return children (according to fractal type)
    std::vector<Ptr> subdivide(FractalType ft, int& nextId) {
        if (subdivided) return children;
        auto subRects = rect.subdivide(ft);
        children.reserve(subRects.size());
        for (auto& sr : subRects)
            children.push_back(std::make_shared<Cell>(nextId++, sr, depth + 1));
        subdivided = true;
        return children;
    }
};

// ============================================================================
// Expanding Topology Graph
// ============================================================================
class FractalTopologyGraph {
public:
    using CellPtr = Cell::Ptr;
    using CellWeakPtr = Cell::WeakPtr;

    std::unordered_map<int, CellPtr> nodes;
    int nextId = 0;
    FractalType fractalType;
    TopologyExpansion expansionRule;
    mutable std::mutex mutex;

    FractalTopologyGraph(FractalType ft, TopologyExpansion exp)
        : fractalType(ft), expansionRule(exp) {}

    CellPtr addRoot(const Rectangle& rect) {
        auto cell = std::make_shared<Cell>(nextId++, rect, 0);
        nodes[cell->id] = cell;
        return cell;
    }

    // Expand a cell: subdivide and rewire edges according to the chosen expansion
    void expandCell(CellPtr cell) {
        if (!cell || cell->subdivided) return;

        // Subdivide
        int dummy = nextId; // temporary; subdivide just creates children without registering
        auto children = cell->subdivide(fractalType, dummy);
        for (auto& ch : children) {
            ch->id = nextId++;
            nodes[ch->id] = ch;
        }

        // Remove original cell from nodes
        nodes.erase(cell->id);

        // Rewire neighbours
        if (expansionRule == TopologyExpansion::Standard) {
            rewireStandard(cell, children);
        } else {
            rewireEdgePreserving(cell, children);
        }

        // Build internal edges among children (they are adjacent)
        for (size_t i = 0; i < children.size(); ++i) {
            for (size_t j = i+1; j < children.size(); ++j) {
                for (int dir = 0; dir < 4; ++dir) {
                    if (children[i]->rect.adjacent(children[j]->rect, dir)) {
                        children[i]->neighbours[dir].push_back(children[j]);
                        children[j]->neighbours[(dir+2)%4].push_back(children[i]);
                        break;   // one direction is enough
                    }
                }
            }
        }
    }

private:
    // Standard: each external neighbour connects to all boundary children it touches
    void rewireStandard(CellPtr original, const std::vector<CellPtr>& children) {
        for (int dir = 0; dir < 4; ++dir) {
            for (auto& neigh : original->neighbours[dir]) {
                for (auto& ch : children) {
                    if (ch->rect.adjacent(neigh->rect, dir)) {
                        ch->neighbours[dir].push_back(neigh);
                        // Replace original cell in neighbour's adjacency
                        auto& neighList = neigh->neighbours[(dir+2)%4];
                        auto it = std::find(neighList.begin(), neighList.end(), original);
                        if (it != neighList.end()) *it = ch;
                        else neighList.push_back(ch);
                    }
                }
            }
        }
    }

    // Edge-preserving: only the closest boundary child along the normal direction is chosen
    void rewireEdgePreserving(CellPtr original, const std::vector<CellPtr>& children) {
        for (int dir = 0; dir < 4; ++dir) {
            for (auto& neigh : original->neighbours[dir]) {
                // Find the child that is centred along the face (closest to edge centre)
                double target = (dir % 2 == 0) 
                    ? (neigh->rect.ymin + neigh->rect.ymax) / 2.0   // left/right: match y
                    : (neigh->rect.xmin + neigh->rect.xmax) / 2.0; // top/bottom: match x
                CellPtr best = nullptr;
                double bestDist = std::numeric_limits<double>::max();
                for (auto& ch : children) {
                    if (!ch->rect.adjacent(neigh->rect, dir)) continue;
                    double centre = (dir % 2 == 0)
                        ? (ch->rect.ymin + ch->rect.ymax) / 2.0
                        : (ch->rect.xmin + ch->rect.xmax) / 2.0;
                    double dist = std::abs(centre - target);
                    if (dist < bestDist) {
                        bestDist = dist;
                        best = ch;
                    }
                }
                if (best) {
                    best->neighbours[dir].push_back(neigh);
                    auto& neighList = neigh->neighbours[(dir+2)%4];
                    auto it = std::find(neighList.begin(), neighList.end(), original);
                    if (it != neighList.end()) *it = best;
                    else neighList.push_back(best);
                }
            }
        }
    }
};

// ============================================================================
// Fractal generation & topology extraction
// ============================================================================
template<FractalType ft, TopologyExpansion exp>
class FractalGenerator {
public:
    FractalGenerator(int maxDepth) : maxDepth_(maxDepth), graph_(ft, exp) {
        root_ = graph_.addRoot(Rectangle(0,0,1,1));
    }

    // Execute subdivision up to maxDepth
    void run() {
        subdivideRecursive(root_, 0);
    }

    // Get all leaf cells (the fractal approximation)
    std::vector<Cell::Ptr> leafCells() const {
        std::vector<Cell::Ptr> leaves;
        for (const auto& [id, cell] : graph_.nodes)
            if (!cell->subdivided)
                leaves.push_back(cell);
        return leaves;
    }

    // Build the topology from the leaf cells (as a basis for the induced topology)
    Topology<Rectangle> inducedTopology() const {
        std::set<Rectangle> basis;
        for (auto& cell : leafCells())
            basis.insert(cell->rect);
        return Topology<Rectangle>(basis);
    }

    // ASCII render of the fractal (using a bitmap)
    std::string renderASCII(int resolution = 81) const {
        std::vector<char> pixels(resolution * resolution, ' ');
        for (auto& cell : leafCells()) {
            int ix0 = std::clamp(int(cell->rect.xmin * resolution), 0, resolution-1);
            int ix1 = std::clamp(int(cell->rect.xmax * resolution), 0, resolution-1);
            int iy0 = std::clamp(int(cell->rect.ymin * resolution), 0, resolution-1);
            int iy1 = std::clamp(int(cell->rect.ymax * resolution), 0, resolution-1);
            for (int y = iy0; y < iy1; ++y)
                for (int x = ix0; x < ix1; ++x)
                    pixels[y * resolution + x] = '#';
        }
        std::ostringstream oss;
        for (int y = resolution-1; y >= 0; --y) {
            for (int x = 0; x < resolution; ++x)
                oss << pixels[y * resolution + x];
            oss << '\n';
        }
        return oss.str();
    }

    // Print graph statistics
    void printStats() const {
        auto leaves = leafCells();
        std::cout << std::format("Fractal: {} | Topology: {} | Depth: {}",
                                 fractal_name(ft), expansion_name(exp), maxDepth_) << "\n";
        std::cout << "Leaf cells: " << leaves.size() << "\n";
        // Count edges
        size_t edges = 0;
        for (auto& cell : leaves)
            for (int d = 0; d < 4; ++d)
                edges += cell->neighbours[d].size();
        std::cout << "Total edges: " << edges / 2 << "\n";   // each edge counted twice
    }

private:
    int maxDepth_;
    FractalTopologyGraph graph_;
    Cell::Ptr root_;

    void subdivideRecursive(Cell::Ptr cell, int depth) {
        if (depth >= maxDepth_) return;
        graph_.expandCell(cell);

        // Parallelize children
        std::vector<std::future<void>> futures;
        for (auto& child : cell->children) {
            futures.push_back(std::async(std::launch::async,
                [this, child, depth]() {
                    subdivideRecursive(child, depth + 1);
                }));
        }
        for (auto& f : futures) f.get();
    }
};

// ============================================================================
// Usage demo
// ============================================================================
int main() {
    // Choose your fractal and expansion at compile‑time via templates
    // Here we instantiate three different configurations and compare them.

    std::cout << "=== Fractal & Topology Demo (C++20 enum-driven) ===\n\n";

    // Configuration 1: Sierpinski Carpet with Standard expansion, depth 3
    FractalGenerator<FractalType::SierpinskiCarpet, TopologyExpansion::Standard> gen1(3);
    gen1.run();
    gen1.printStats();
    std::cout << "Induced topology size (open sets): " << gen1.inducedTopology().size() << "\n";
    std::cout << gen1.renderASCII(27) << "\n\n";

    // Configuration 2: Vicsek Cross with Edge-Preserving expansion, depth 4
    FractalGenerator<FractalType::VicsekCross, TopologyExpansion::EdgePreserving> gen2(4);
    gen2.run();
    gen2.printStats();
    std::cout << "Induced topology size: " << gen2.inducedTopology().size() << "\n";
    std::cout << gen2.renderASCII(81) << "\n\n";

    // Configuration 3: Cantor Dust, depth 5 (very sparse)
    FractalGenerator<FractalType::CantorDust, TopologyExpansion::Standard> gen3(5);
    gen3.run();
    gen3.printStats();
    std::cout << "Induced topology size: " << gen3.inducedTopology().size() << "\n";
    std::cout << gen3.renderASCII(64) << "\n\n";

    // Print adjacency of a few leaves from gen1
    auto leaves = gen1.leafCells();
    std::cout << "Sample adjacency (first 3 leaf cells from gen1):\n";
    for (size_t i = 0; i < std::min(leaves.size(), size_t(3)); ++i) {
        auto& cell = leaves[i];
        std::cout << "Cell " << cell->id << " (rect ["
                  << cell->rect.xmin << "," << cell->rect.ymin << "]-["
                  << cell->rect.xmax << "," << cell->rect.ymax << "]):\n";
        for (int d = 0; d < 4; ++d) {
            const char* dir[] = {"L", "R", "B", "T"};
            std::cout << "  " << dir[d] << ": ";
            for (auto& n : cell->neighbours[d])
                std::cout << n->id << " ";
            std::cout << "\n";
        }
    }

    return 0;
}