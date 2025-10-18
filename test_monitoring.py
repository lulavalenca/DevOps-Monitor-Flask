# Script de teste para identificar o problema no monitoring.py

print("🔍 Testando componentes do sistema...")
print("=" * 60)

# Teste 1: Imports
print("\n1. Testando imports...")
try:
    import psutil

    print("  ✅ psutil importado com sucesso")
except Exception as e:
    print(f"  ❌ Erro ao importar psutil: {e}")

try:
    import platform

    print("  ✅ platform importado com sucesso")
except Exception as e:
    print(f"  ❌ Erro ao importar platform: {e}")

# Teste 2: Monitoramento
print("\n2. Testando SystemMonitor...")
try:
    from monitoring import SystemMonitor

    print("  ✅ SystemMonitor importado")

    monitor = SystemMonitor()
    print("  ✅ SystemMonitor instanciado")

    # Teste 3: Coleta de métricas
    print("\n3. Testando coleta de métricas...")

    # CPU
    try:
        cpu = monitor.get_cpu_usage()
        print(f"  ✅ CPU: {cpu}%")
    except Exception as e:
        print(f"  ❌ Erro CPU: {e}")

    # Memória
    try:
        memory = monitor.get_memory_usage()
        print(f"  ✅ Memória: {memory['percentage']}%")
    except Exception as e:
        print(f"  ❌ Erro Memória: {e}")

    # Disco
    try:
        disk = monitor.get_disk_usage()
        print(f"  ✅ Disco: {disk['percentage']:.1f}%")
    except Exception as e:
        print(f"  ❌ Erro Disco: {e}")

    # Rede
    try:
        network = monitor.get_network_stats()
        print(f"  ✅ Rede: {network['bytes_recv']} bytes recebidos")
    except Exception as e:
        print(f"  ❌ Erro Rede: {e}")

    # System Info - ESTE É O PROBLEMA!
    print("\n4. Testando system_info (PROVÁVEL PROBLEMA)...")
    try:
        system_info = monitor.get_system_info()
        print(f"  ✅ System Info:")
        print(f"     • Hostname: {system_info['hostname']}")
        print(f"     • Platform: {system_info['platform']}")
        print(f"     • CPUs: {system_info['cpu_count']}")
        print(f"     • Uptime: {system_info['uptime']}")
    except Exception as e:
        print(f"  ❌ Erro System Info: {e}")
        print(f"     Tipo do erro: {type(e).__name__}")
        import traceback

        traceback.print_exc()

    # Teste 5: Todas as métricas
    print("\n5. Testando get_all_metrics()...")
    try:
        metrics = monitor.get_all_metrics()
        print(f"  ✅ Métricas coletadas com sucesso!")
        print(f"     • CPU: {metrics['cpu']}%")
        print(f"     • Memória: {metrics['memory']['percentage']}%")
        print(f"     • Disco: {metrics['disk']['percentage']:.1f}%")
    except Exception as e:
        print(f"  ❌ Erro ao coletar métricas: {e}")
        print(f"     Tipo do erro: {type(e).__name__}")
        import traceback

        traceback.print_exc()

except Exception as e:
    print(f"  ❌ Erro ao importar/usar SystemMonitor: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("🏁 Teste concluído!")
