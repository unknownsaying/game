// VRWorld.cs
// Single-file, clean, extensible VR world for Steam (Unity + SteamVR + Steamworks.NET)
// Attach to an empty GameObject in your scene.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Steamworks;
using Steamworks.Data;
using UnityEngine;
using Valve.VR;
using UnityEngine.XR.Interaction.Toolkit;

// ============================================
// 1. CORE INTERFACES (Extension Points)
// ============================================
public interface IVRWorldExtension
{
    string Name { get; }
    int Priority { get; }
    void Initialize(ServiceLocator services);
    void Shutdown();
}

public interface IWorldGenerator
{
    void Generate(Transform root);
    void Clear();
}

public interface INetworkService
{
    uint AppId { get; set; }
    void Init();
    void Shutdown();
    void HostLobby();
    void JoinLobby(SteamId id);
    void Broadcast(byte[] data);
    event Action<ulong, byte[]> OnData;
}

public interface IObjectPool
{
    event Action<GameObject> OnObjectCreated;
    GameObject Get();
    void Return(GameObject obj);
}

// ============================================
// 2. SERVICE LOCATOR (Simple DI Container)
// ============================================
public class ServiceLocator
{
    private readonly Dictionary<Type, object> services = new();
    private readonly Dictionary<(Type, string), object> tagged = new();

    public void Register<T>(T service) => services[typeof(T)] = service;
    public void Register<T>(T service, string tag) => tagged[(typeof(T), tag)] = service;
    public T Get<T>() where T : class => services.TryGetValue(typeof(T), out var s) ? s as T : null;
    public T Get<T>(string tag) where T : class => tagged.TryGetValue((typeof(T), tag), out var s) ? s as T : null;
}

// ============================================
// 3. CORE SERVICES (Concrete Implementations)
// ============================================
public class SteamNetworkService : INetworkService, IDisposable
{
    public uint AppId { get; set; } = 480;
    public event Action<ulong, byte[]> OnData;

    private SocketManager socket;
    private ConnectionManager connManager;

    public void Init()
    {
        SteamClient.Init(AppId);
        Debug.Log($"[Steam] Initialized with AppId {AppId}");
    }

    public void Shutdown()
    {
        socket?.Close();
        SteamClient.Shutdown();
    }

    public void HostLobby()
    {
        SteamMatchmaking.CreateLobbyAsync(4).ContinueWith(t =>
        {
            if (t.IsCompletedSuccessfully)
            {
                var lobby = t.Result;
                lobby.SetPublic();
                lobby.SetJoinable(true);
                lobby.SetData("game", "vr_world");
                socket = SteamNetworkingSockets.CreateRelaySocket<SocketManager>(0);
                Debug.Log($"[Lobby] Hosting lobby {lobby.Id}");
            }
        });
    }

    public void JoinLobby(SteamId id)
    {
        SteamMatchmaking.JoinLobbyAsync(id);
        // Connection setup simplified; a full version would create ConnectionManager
    }

    public void Broadcast(byte[] data)
    {
        socket?.Connection?.SendMessage(data);
    }

    class SocketManager : Steamworks.SocketManager
    {
        public override void OnMessage(Connection connection, IntPtr data, int size)
        {
            byte[] bytes = new byte[size];
            System.Runtime.InteropServices.Marshal.Copy(data, bytes, 0, size);
            (SteamNetworkingSockets.Current as SteamNetworkService)?.OnData?.Invoke(connection.Id, bytes);
        }
    }
}

public class ObjectPoolService : IObjectPool
{
    private readonly Queue<GameObject> pool = new();
    private readonly GameObject prefab;
    public event Action<GameObject> OnObjectCreated;

    public ObjectPoolService(GameObject prefab, int initialSize = 20)
    {
        this.prefab = prefab;
        for (int i = 0; i < initialSize; i++) CreateNew();
    }

    private void CreateNew()
    {
        var obj = UnityEngine.Object.Instantiate(prefab);
        obj.SetActive(false);
        pool.Enqueue(obj);
    }

    public GameObject Get()
    {
        var obj = pool.Count > 0 ? pool.Dequeue() : UnityEngine.Object.Instantiate(prefab);
        obj.SetActive(true);
        OnObjectCreated?.Invoke(obj);
        return obj;
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}

public class SteamVRInputService
{
    public bool GetBool(SteamVR_Action_Boolean action, SteamVR_Input_Sources source = SteamVR_Input_Sources.Any)
        => action.GetState(source);
    public Vector2 GetAxis(SteamVR_Action_Vector2 action, SteamVR_Input_Sources source = SteamVR_Input_Sources.Any)
        => action.GetAxis(source);
}

// ============================================
// 4. EXTENSION MANAGER
// ============================================
public class ExtensionManager
{
    private readonly List<IVRWorldExtension> extensions = new();
    private readonly ServiceLocator services;

    public ExtensionManager(ServiceLocator services) => this.services = services;

    public void Register(IVRWorldExtension ext) => extensions.Add(ext);

    public void InitializeAll()
    {
        foreach (var ext in extensions.OrderBy(e => e.Priority))
        {
            Debug.Log($"[VRWorld] Loading: {ext.Name}");
            ext.Initialize(services);
        }
    }

    public void ShutdownAll()
    {
        foreach (var ext in extensions) ext.Shutdown();
    }
}

// ============================================
// 5. BUILT-IN EXTENSIONS
// ============================================

// ----- Fractal City Generator -----
public class FractalCityGenerator : MonoBehaviour, IVRWorldExtension, IWorldGenerator
{
    public string Name => "Fractal City";
    public int Priority => 10;

    [Header("Fractal Settings")]
    [SerializeField] private int depth = 3;
    [SerializeField] private Material buildingMaterial;

    private ServiceLocator services;
    private GameObject worldRoot;

    public void Initialize(ServiceLocator services)
    {
        this.services = services;
        services.Register<IWorldGenerator>(this);
        Generate(null);
    }

    public void Generate(Transform root)
    {
        worldRoot = new GameObject("FractalCity");
        if (root) worldRoot.transform.SetParent(root);
        BuildRecursive(worldRoot.transform, Vector3.zero, 20f, depth);
    }

    private void BuildRecursive(Transform parent, Vector3 pos, float size, int depth)
    {
        if (depth == 0)
        {
            CreateBlock(parent, pos, size);
            return;
        }
        float step = size / 3f;
        for (int x = 0; x < 3; x++)
        for (int y = 0; y < 3; y++)
        for (int z = 0; z < 3; z++)
        {
            if (x == 1 && y == 1 && z == 1) continue;
            Vector3 subPos = pos + new Vector3((x - 1) * step, (y - 1) * step, (z - 1) * step);
            BuildRecursive(parent, subPos, step, depth - 1);
        }
    }

    private void CreateBlock(Transform parent, Vector3 pos, float size)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
        go.transform.position = pos;
        go.transform.localScale = Vector3.one * size;
        go.transform.SetParent(parent);
        if (buildingMaterial) go.GetComponent<Renderer>().material = buildingMaterial;
        var rb = go.AddComponent<Rigidbody>();
        rb.mass = size;
        rb.isKinematic = true; // Start static; later made dynamic if grabbed
    }

    public void Clear()
    {
        if (worldRoot) Destroy(worldRoot);
    }

    public void Shutdown() => Clear();
}

// ----- Throwable Interaction Extension -----
public class ThrowableInteraction : MonoBehaviour, IVRWorldExtension
{
    public string Name => "Throwable Objects";
    public int Priority => 20;

    private ServiceLocator services;
    private XRInteractionManager interactionManager;

    public void Initialize(ServiceLocator services)
    {
        this.services = services;
        interactionManager = new GameObject("InteractionManager").AddComponent<XRInteractionManager>();
        var pool = services.Get<IObjectPool>();
        if (pool != null) pool.OnObjectCreated += MakeGrabbable;
        // Also process existing world blocks
        foreach (var col in FindObjectsOfType<Collider>())
            MakeGrabbable(col.gameObject);
    }

    private void MakeGrabbable(GameObject obj)
    {
        if (obj.GetComponent<XRGrabInteractable>() == null)
        {
            var grab = obj.AddComponent<XRGrabInteractable>();
            grab.throwOnDetach = true;
            // Freeze/unfreeze physics on grab
            grab.selectEntered.AddListener(_ =>
            {
                if (obj.TryGetComponent<Rigidbody>(out var rb)) rb.isKinematic = false;
                if (obj.TryGetComponent<Collider>(out var col)) col.isTrigger = false;
            });
            grab.selectExited.AddListener(_ =>
            {
                // Haptic feedback
                if (grab.interactorsSelecting.Count > 0 &&
                    grab.interactorsSelecting[0] is XRBaseControllerInteractor controller)
                    controller.SendHapticImpulse(0.8f, 0.13f);
            });
        }
    }

    public void Shutdown()
    {
        var pool = services.Get<IObjectPool>();
        if (pool != null) pool.OnObjectCreated -= MakeGrabbable;
        if (interactionManager) Destroy(interactionManager.gameObject);
    }
}

// ----- Simple NPC Spawner (Example) -----
public class NPCSpawnerExtension : MonoBehaviour, IVRWorldExtension
{
    public string Name => "NPC Spawner";
    public int Priority => 30;

    [SerializeField] private GameObject npcPrefab;

    public void Initialize(ServiceLocator services)
    {
        var network = services.Get<INetworkService>();
        if (network == null) return;
        // Only host spawns NPCs
        network.HostLobby(); // Simplified – real code would have lobby logic
        SpawnNPCs();
    }

    private void SpawnNPCs()
    {
        for (int i = 0; i < 10; i++)
        {
            var npc = Instantiate(npcPrefab ?? GameObject.CreatePrimitive(PrimitiveType.Sphere),
                UnityEngine.Random.insideUnitSphere * 30f + Vector3.up,
                Quaternion.identity);
            npc.name = $"NPC_{i}";
            npc.AddComponent<NetworkSyncedTransform>();
        }
    }

    public void Shutdown() { }
}

// ----- Multiplayer Sync Extension -----
public class NetworkSyncExtension : MonoBehaviour, IVRWorldExtension
{
    public string Name => "Multiplayer Sync";
    public int Priority => 1; // early

    public void Initialize(ServiceLocator services)
    {
        var network = services.Get<INetworkService>();
        network?.Init();
    }

    public void Shutdown()
    {
        var network = services?.Get<INetworkService>();
        network?.Shutdown();
    }
}

// ----- Network Synced Transform (Simple) -----
public class NetworkSyncedTransform : MonoBehaviour
{
    [SerializeField] private float lerpSpeed = 10f;
    private Vector3 targetPos;
    private Quaternion targetRot;

    private void Start() => InvokeRepeating(nameof(Sync), 0f, 0.05f);

    private void Update()
    {
        transform.position = Vector3.Lerp(transform.position, targetPos, Time.deltaTime * lerpSpeed);
        transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, Time.deltaTime * lerpSpeed);
    }

    private void Sync()
    {
        targetPos = transform.position;
        targetRot = transform.rotation;
    }
}

// ============================================
// 6. MAIN VRWORLD BOOTSTRAPPER (Attach this)
// ============================================
public class VRWorldBootstrap : MonoBehaviour
{
    [Header("Extensions (any script implementing IVRWorldExtension)")]
    public List<MonoBehaviour> extensionPrefabs = new();

    private ServiceLocator services;
    private ExtensionManager extensions;

    private void Awake()
    {
        // Setup service locator
        services = new ServiceLocator();

        // Register core services
        var input = new SteamVRInputService();
        services.Register(input);

        var network = new SteamNetworkService { AppId = 480 };
        services.Register<INetworkService>(network);

        // Simple object pool with a cube prefab
        var poolPrefab = GameObject.CreatePrimitive(PrimitiveType.Cube);
        poolPrefab.SetActive(false);
        var pool = new ObjectPoolService(poolPrefab, 10);
        services.Register<IObjectPool>(pool);

        // Load extensions
        extensions = new ExtensionManager(services);
        foreach (var prefab in extensionPrefabs)
        {
            var instance = Instantiate(prefab, transform);
            if (instance is IVRWorldExtension ext)
                extensions.Register(ext);
        }
        extensions.InitializeAll();

        Debug.Log("[VRWorld] Bootstrapped successfully.");
    }

    private void OnDestroy()
    {
        extensions?.ShutdownAll();
    }
}
// ============================================
// 7. USAGE INSPECTOR HELPER
// ============================================
#if UNITY_EDITOR
[UnityEditor.CustomEditor(typeof(VRWorldBootstrap))]
public class VRWorldBootstrapEditor : UnityEditor.Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        UnityEditor.EditorGUILayout.HelpBox(
            "Drag GameObjects with IVRWorldExtension scripts here.\n" +
            "Extensions are initialized in priority order.",
            UnityEditor.MessageType.Info);

        if (GUILayout.Button("Find Extensions in Scene"))
        {
            var bootstrap = target as VRWorldBootstrap;
            bootstrap.extensionPrefabs.Clear();
            foreach (var ext in FindObjectsOfType<MonoBehaviour>().OfType<IVRWorldExtension>())
                bootstrap.extensionPrefabs.Add(ext as MonoBehaviour);
            UnityEditor.EditorUtility.SetDirty(bootstrap);
        }
    }
}
#endif
