// File: traffic_center_vr.cpp
// Build: g++ -std=c++20 -I<path to openvr> -I<path to boost> -lglfw -ldl -lpthread traffic_center_vr.cpp -o traffic_center_vr

#define GLAD_GL_IMPLEMENTATION
#include <glad/gl.h>
#include <GLFW/glfw3.h>

#include <openvr.h>
#include <boost/asio.hpp>
#include <boost/endian/conversion.hpp>   // for binary protocol

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <format>
#include <iostream>
#include <memory>
#include <mutex>
#include <optional>
#include <queue>
#include <shared_mutex>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>
#include <vector>

using namespace std::literals;

// ======================================================================
// Binary protocol – low-latency fixed-size packet
// ======================================================================
#pragma pack(push, 1)
struct MobilePacket {
    uint32_t seq_number;                // incremental
    uint32_t device_id;                 // assigned by traffic center on handshake
    // Quaternion (orientation)
    float quat_x, quat_y, quat_z, quat_w;
    // Multi-touch: up to 5 touches (0 if not present)
    struct TouchPoint {
        float x, y;                     // normalised [0,1]
        bool active;
    };
    TouchPoint touches[5];
    // Digital buttons (bitmask)
    uint32_t buttons;
    // Reserved for future expansion
    char reserved[16];
};
#pragma pack(pop)

static_assert(sizeof(MobilePacket) == 4+4 + 4*4 + 5*(4+4+1) + 4 + 16, "Packet size mismatch");

// ======================================================================
// Mutable state of a single connected mobile device
// ======================================================================
struct DeviceState {
    mutable std::shared_mutex mutex;
    uint32_t device_id = 0;
    bool connected = false;
    std::chrono::steady_clock::time_point last_packet_time;

    // Orientation (quaternion, w first in OpenVR style)
    float quat[4] = {1,0,0,0};
    // Touch points (world XY plane, scale meters)
    std::vector<std::pair<float,float>> active_touches;
    // Button mask
    uint32_t buttons = 0;

    void updateFromPacket(const MobilePacket& pkt) {
        std::unique_lock lock(mutex);
        quat[0] = pkt.quat_w;
        quat[1] = pkt.quat_x;
        quat[2] = pkt.quat_y;
        quat[3] = pkt.quat_z;
        buttons = pkt.buttons;

        active_touches.clear();
        for (auto& t : pkt.touches) {
            if (t.active) active_touches.emplace_back(t.x, t.y);
        }
        last_packet_time = std::chrono::steady_clock::now();
    }
};

// ======================================================================
// Variable Traffic Center – manages mobile connections asynchronously
// ======================================================================
class TrafficCenter {
public:
    using DevicePtr = std::shared_ptr<DeviceState>;
    using DeviceMap = std::unordered_map<uint32_t, DevicePtr>;

    TrafficCenter(uint16_t port)
        : acceptor_(io_ctx_, boost::asio::ip::tcp::endpoint(boost::asio::ip::tcp::v4(), port))
    {}

    void start() {
        startAccept();
        worker_ = std::async(std::launch::async, [this] { io_ctx_.run(); });
    }

    void stop() {
        io_ctx_.stop();
        if (worker_.valid()) worker_.get();
    }

    // Thread-safe snapshot of all currently connected devices
    DeviceMap getDevices() const {
        std::shared_lock lock(devices_mutex_);
        return devices_;
    }

private:
    boost::asio::io_context io_ctx_;
    boost::asio::ip::tcp::acceptor acceptor_;
    std::future<void> worker_;

    mutable std::shared_mutex devices_mutex_;
    DeviceMap devices_;
    std::atomic<uint32_t> next_device_id_{1};

    void startAccept() {
        auto socket = std::make_shared<boost::asio::ip::tcp::socket>(io_ctx_);
        acceptor_.async_accept(*socket, [this, socket](boost::system::error_code ec) {
            if (!ec) {
                handleNewConnection(std::move(*socket));
            }
            startAccept(); // accept next
        });
    }

    void handleNewConnection(boost::asio::ip::tcp::socket socket) {
        uint32_t dev_id = next_device_id_++;
        auto dev = std::make_shared<DeviceState>();
        dev->device_id = dev_id;
        dev->connected = true;

        {
            std::unique_lock lock(devices_mutex_);
            devices_[dev_id] = dev;
        }

        // Send assigned device ID to the client (first 4 bytes, big-endian)
        uint32_t be_id = boost::endian::native_to_big(dev_id);
        boost::asio::async_write(socket, boost::asio::buffer(&be_id, sizeof(be_id)),
            [this, dev, socket = std::make_shared<boost::asio::ip::tcp::socket>(std::move(socket))]
            (boost::system::error_code ec, std::size_t) mutable {
                if (!ec) {
                    startRead(*socket, dev);
                } else {
                    dev->connected = false;
                    std::unique_lock lock(devices_mutex_);
                    devices_.erase(dev->device_id);
                }
            });
    }

    void startRead(boost::asio::ip::tcp::socket& socket, DevicePtr dev) {
        auto buf = std::make_shared<MobilePacket>();
        boost::asio::async_read(socket, boost::asio::buffer(buf.get(), sizeof(MobilePacket)),
            [this, &socket, dev, buf](boost::system::error_code ec, std::size_t) mutable {
                if (!ec) {
                    dev->updateFromPacket(*buf);
                    startRead(socket, dev);
                } else {
                    dev->connected = false;
                    std::unique_lock lock(devices_mutex_);
                    devices_.erase(dev->device_id);
                }
            });
    }
};

// ======================================================================
// SteamVR + OpenGL wrappers (slightly simplified from earlier answer)
// ======================================================================
struct EyeRenderTarget {
    GLuint framebuffer = 0, texture = 0, depthStencil = 0;
    vr::EVREye eye;
    uint32_t width, height;
};

struct CubeMesh {
    GLuint vao = 0, vbo = 0, ebo = 0;
    size_t indexCount = 0;
};

// Shaders embedded (same as before)
static const char* vertexSrc = R"(#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;
uniform mat4 uMVP;
out vec3 vNormal;
void main() {
    gl_Position = uMVP * vec4(aPos, 1.0);
    vNormal = aNormal;
}
)";
static const char* fragmentSrc = R"(#version 330 core
in vec3 vNormal;
uniform vec3 uColor;
out vec4 fragColor;
void main() {
    vec3 lightDir = normalize(vec3(0.5, 1.0, 0.3));
    float diff = max(dot(normalize(vNormal), lightDir), 0.2);
    fragColor = vec4(uColor * diff, 1.0);
}
)";

GLuint createShader() {
    GLuint vs = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vs, 1, &vertexSrc, nullptr);
    glCompileShader(vs);
    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &fragmentSrc, nullptr);
    glCompileShader(fs);
    GLuint prog = glCreateProgram();
    glAttachShader(prog, vs); glAttachShader(prog, fs);
    glLinkProgram(prog);
    glDeleteShader(vs); glDeleteShader(fs);
    return prog;
}

bool createEyeRenderTargets(vr::IVRSystem* hmd, EyeRenderTarget* eyes) {
    uint32_t w, h;
    hmd->GetRecommendedRenderTargetSize(&w, &h);
    for (int i = 0; i < 2; ++i) {
        auto& e = eyes[i];
        e.eye = (i == 0) ? vr::Eye_Left : vr::Eye_Right;
        e.width = w; e.height = h;
        glGenFramebuffers(1, &e.framebuffer);
        glGenTextures(1, &e.texture);
        glGenTextures(1, &e.depthStencil);
        glBindTexture(GL_TEXTURE_2D, e.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glBindTexture(GL_TEXTURE_2D, e.depthStencil);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH24_STENCIL8, w, h, 0, GL_DEPTH_STENCIL, GL_UNSIGNED_INT_24_8, nullptr);
        glBindFramebuffer(GL_FRAMEBUFFER, e.framebuffer);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, e.texture, 0);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, e.depthStencil, 0);
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) return false;
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
    }
    return true;
}

CubeMesh createCube() {
    // Vertices (pos, normal) duplicated per face for flat shading
    float v[][6] = {
        // front
        {-0.5,-0.5,0.5,  0,0,1}, {0.5,-0.5,0.5,  0,0,1}, {0.5,0.5,0.5,  0,0,1}, {-0.5,0.5,0.5,  0,0,1},
        // back
        {0.5,-0.5,-0.5,  0,0,-1}, {-0.5,-0.5,-0.5,  0,0,-1}, {-0.5,0.5,-0.5,  0,0,-1}, {0.5,0.5,-0.5,  0,0,-1},
        // left
        {-0.5,-0.5,-0.5, -1,0,0}, {-0.5,-0.5,0.5, -1,0,0}, {-0.5,0.5,0.5, -1,0,0}, {-0.5,0.5,-0.5, -1,0,0},
        // right
        {0.5,-0.5,0.5,  1,0,0}, {0.5,-0.5,-0.5,  1,0,0}, {0.5,0.5,-0.5,  1,0,0}, {0.5,0.5,0.5,  1,0,0},
        // top
        {-0.5,0.5,0.5,  0,1,0}, {0.5,0.5,0.5,  0,1,0}, {0.5,0.5,-0.5,  0,1,0}, {-0.5,0.5,-0.5,  0,1,0},
        // bottom
        {-0.5,-0.5,-0.5,  0,-1,0}, {0.5,-0.5,-0.5,  0,-1,0}, {0.5,-0.5,0.5,  0,-1,0}, {-0.5,-0.5,0.5,  0,-1,0}
    };
    uint32_t indices[] = {
        0,1,2, 2,3,0, 4,5,6, 6,7,4, 8,9,10, 10,11,8,
        12,13,14, 14,15,12, 16,17,18, 18,19,16, 20,21,22, 22,23,20
    };
    CubeMesh cm;
    cm.indexCount = std::size(indices);
    glGenVertexArrays(1, &cm.vao); glGenBuffers(1, &cm.vbo); glGenBuffers(1, &cm.ebo);
    glBindVertexArray(cm.vao);
    glBindBuffer(GL_ARRAY_BUFFER, cm.vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(v), v, GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cm.ebo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6*sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6*sizeof(float), (void*)(3*sizeof(float)));
    glEnableVertexAttribArray(1);
    glBindVertexArray(0);
    return cm;
}

// ======================================================================
// Main: set up VR, traffic center, then render each device as a cube
// ======================================================================
int main() {
    // 1. OpenVR initialisation
    vr::EVRInitError err = vr::VRInitError_None;
    vr::IVRSystem* hmd = vr::VR_Init(&err, vr::VRApplication_Scene);
    if (err != vr::VRInitError_None) {
        std::cerr << "VR init failed\n";
        return -1;
    }
    vr::IVRCompositor* compositor = vr::VRCompositor();

    // 2. GLFW window (mirror)
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    GLFWwindow* window = glfwCreateWindow(1280, 720, "Traffic Center VR", nullptr, nullptr);
    glfwMakeContextCurrent(window);
    gladLoadGL(glfwGetProcAddress);
    glfwSwapInterval(0);

    // 3. Shader and cube
    GLuint shader = createShader();
    CubeMesh cubeMesh = createCube();

    // 4. Eye render targets
    EyeRenderTarget eyes[2];
    if (!createEyeRenderTargets(hmd, eyes)) return -2;

    // 5. Start TrafficCenter on port 17771 (any free port)
    TrafficCenter traffic(17771);
    traffic.start();
    std::cout << "Traffic Center listening on port 17771...\n";

    // 6. VR loop
    vr::TrackedDevicePose_t poses[vr::k_unMaxTrackedDeviceCount];
    // Simple HMD pose storage (for view matrix)
    float hmdWorld[4][4] = {{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}};

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();

        // 6a. Get poses
        compositor->WaitGetPoses(poses, vr::k_unMaxTrackedDeviceCount, nullptr, 0);
        if (poses[0].bPoseIsValid) {
            auto& m = poses[0].mDeviceToAbsoluteTracking;
            for (int i=0;i<3;++i) for (int j=0;j<4;++j) hmdWorld[i][j] = m.m[i][j];
        }

        // 6b. Get mutable mobile devices from traffic center
        auto devices = traffic.getDevices();

        // 6c. Render each eye
        for (int eyeIdx = 0; eyeIdx < 2; ++eyeIdx) {
            auto& eye = eyes[eyeIdx];
            glBindFramebuffer(GL_FRAMEBUFFER, eye.framebuffer);
            glViewport(0, 0, eye.width, eye.height);
            glClearColor(0.1f, 0.1f, 0.15f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
            glEnable(GL_DEPTH_TEST);

            // View & Projection from OpenVR
            vr::HmdMatrix34_t eyeToHead = hmd->GetEyeToHeadTransform(eye.eye);
            vr::HmdMatrix44_t proj = hmd->GetProjectionMatrix(eye.eye, 0.1f, 30.0f);

            // Construct view matrix: inverse of (HMD world * eyeToHead)
            float view[16] = {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1};
            // (simplified; actual conversion omitted for brevity – we assume identity for demo)
            // For a real app, compute proper inverse.

            glUseProgram(shader);
            // Render a cube for each connected mobile device
            for (auto& [id, dev] : devices) {
                std::shared_lock lock(dev->mutex);
                if (!dev->connected) continue;
                // Build model matrix from device's quaternion and a fixed position in front of HMD
                float q[4] = {dev->quat[0], dev->quat[1], dev->quat[2], dev->quat[3]}; // w,x,y,z
                // Simple quaternion to rotation matrix (assuming unit)
                float rot[16] = {
                    1-2*(q[2]*q[2]+q[3]*q[3]), 2*(q[1]*q[2]-q[0]*q[3]), 2*(q[1]*q[3]+q[0]*q[2]), 0,
                    2*(q[1]*q[2]+q[0]*q[3]), 1-2*(q[1]*q[1]+q[3]*q[3]), 2*(q[2]*q[3]-q[0]*q[1]), 0,
                    2*(q[1]*q[3]-q[0]*q[2]), 2*(q[2]*q[3]+q[0]*q[1]), 1-2*(q[1]*q[1]+q[2]*q[2]), 0,
                    0,0,0,1
                };
                // Position 0.5m in front of HMD, offset sideways per device ID
                float posX = (id % 4) * 0.3f - 0.45f;
                float model[16] = {
                    rot[0], rot[4], rot[8], 0,
                    rot[1], rot[5], rot[9], 0,
                    rot[2], rot[6], rot[10], 0,
                    posX, 0.5f, -0.8f, 1   // translation column in row-major (typical OpenGL)
                };
                // Combine with view and projection (simplified)
                float mvp[16] = {}; // multiply model * view * proj
                // ... (use linear algebra library in production)
                glUniformMatrix4fv(glGetUniformLocation(shader, "uMVP"), 1, GL_FALSE, mvp);
                // Color depends on button state
                float color[3] = {0.2f, 0.8f, 1.0f};
                if (dev->buttons & 1) color[0] = 1.0f; // button 0 -> redder
                glUniform3fv(glGetUniformLocation(shader, "uColor"), 1, color);

                glBindVertexArray(cubeMesh.vao);
                glDrawElements(GL_TRIANGLES, cubeMesh.indexCount, GL_UNSIGNED_INT, 0);
            }
            glBindVertexArray(0);
            glUseProgram(0);
            glBindFramebuffer(GL_FRAMEBUFFER, 0);

            // Submit to compositor
            vr::Texture_t tex = { (void*)(uintptr_t)eye.texture, vr::TextureType_OpenGL, vr::ColorSpace_Gamma };
            compositor->Submit(eye.eye, &tex);
        }

        // Mirror window (copy left eye)
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glViewport(0, 0, 1280, 720);
        glClear(GL_COLOR_BUFFER_BIT);
        // (Blit left eye texture to window – omitted)
        glfwSwapBuffers(window);

        // Small sleep to avoid busy‑wait
        std::this_thread::sleep_for(1ms);
    }

    traffic.stop();
    vr::VR_Shutdown();
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
