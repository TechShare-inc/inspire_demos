#!/usr/bin/env python3
"""
Stress Test Demo Runner
Demonstrates different stress test scenarios and configurations
"""

import asyncio
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.simple_stress_test import SimpleThroughputTester

SERIAL_PORT = "COM3"  # Adjust for your system
MODBUS_IP = "192.168.11.210"  # Adjust for your system

class StressTestDemo:
    """Demonstration of various stress test scenarios"""
    
    def __init__(self):
        self.tester = None
    
    async def demo_basic_stress_test(self):
        """Demonstrate basic stress testing functionality"""
        print("🎯 DEMO 1: Basic Stress Test")
        print("="*50)
        
        # Create tester (adjust ports as needed)
        self.tester = SimpleThroughputTester(
            serial_port=SERIAL_PORT,  # Adjust for your system
            modbus_ip=MODBUS_IP  # Adjust for your system
        )
        
        print("📋 Running basic latency tests...")
        print("Each test will manage its own connections for clean isolation")
        
        # Test each interface separately (they handle their own connections)
        await self.tester.test_serial_latency(iterations=20)
        
        print("\n⏸️  Brief pause between interface tests...")
        await asyncio.sleep(2)
        
        await self.tester.test_modbus_latency(iterations=20)
        
        # Generate report
        self.tester.print_comprehensive_report()

    async def demo_burst_testing(self):
        """Demonstrate burst testing scenarios"""
        print("\n🚀 DEMO 2: Burst Testing")
        print("="*50)
        
        if not self.tester:
            self.tester = SimpleThroughputTester(
                serial_port=SERIAL_PORT,
                modbus_ip=MODBUS_IP
            )
        
        print("Testing burst capacity...")
        print("Each test manages its own connection for isolation")
        
        # Test burst capacity (methods handle their own connections)
        rate = await self.tester.burst_test("serial", burst_size=30)
        print(f"📊 Serial burst rate: {rate:.1f} ops/sec")
        
        print("⏸️  Brief pause between burst tests...")
        await asyncio.sleep(2)
        
        rate = await self.tester.burst_test("modbus", burst_size=30)
        print(f"📊 Modbus burst rate: {rate:.1f} ops/sec")
    
    async def demo_sustained_load(self):
        """Demonstrate sustained load testing"""
        print("\n⚡ DEMO 3: Sustained Load Testing")
        print("="*50)
        
        if not self.tester:
            self.tester = SimpleThroughputTester(
                serial_port=SERIAL_PORT,
                modbus_ip=MODBUS_IP
            )
        
        print("Running sustained load test (15 seconds)...")
        print("Both Serial and Modbus will be tested sequentially")
        
        # Sustained load test handles its own connections for both interfaces
        await self.tester.sustained_load_test(duration=15, target_rate=3)
        
        print("📈 Sustained load test completed")
        self.tester.print_comprehensive_report()
    
async def interactive_demo():
    """Interactive demonstration menu"""
    demo = StressTestDemo()
    
    print("🧪 COMMUNICATION THROUGHPUT STRESS TEST DEMO")
    print("=" * 60)
    print("This demo shows different stress testing scenarios.")
    print("Ensure your hardware is properly configured before running tests.")
    print()
    
    while True:
        print("\nSelect a demo scenario:")
        print("1. Basic Stress Test (latency measurement)")
        print("2. Burst Testing (maximum short-term throughput)")
        print("3. Sustained Load Test (long-term stability)")
        print("4. Run All Demos")
        print("5. Exit")
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                await demo.demo_basic_stress_test()
            elif choice == "2":
                await demo.demo_burst_testing()
            elif choice == "3":
                await demo.demo_sustained_load()
            elif choice == "4":
                await demo.demo_basic_stress_test()
                await demo.demo_burst_testing()
                await demo.demo_sustained_load()
            elif choice == "5":
                print("👋 Demo completed!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted.")
            break
        except Exception as e:
            print(f"❌ Demo error: {e}")

def print_stress_test_concepts():
    """Print educational content about stress testing"""
    print("\n📚 STRESS TESTING CONCEPTS")
    print("=" * 60)
    print("""
🎯 WHAT IS COMMUNICATION THROUGHPUT STRESS TESTING?

Stress testing evaluates how communication interfaces perform under various
load conditions, helping identify:
• Maximum sustainable data rates
• System bottlenecks and failure points  
• Performance consistency under load
• Resource utilization patterns

🔬 KEY TESTING SCENARIOS:

1. LATENCY CHARACTERIZATION
   • Measures baseline response times
   • Identifies network/protocol overhead
   • Purpose: Establish performance baseline

2. BURST TESTING
   • Maximum short-term throughput
   • Buffer overflow behavior
   • Purpose: Find peak capacity limits

3. SUSTAINED LOAD
   • Long-term performance stability
   • Memory leaks and degradation
   • Purpose: Validate production readiness

4. CONCURRENT ACCESS
   • Multi-interface resource sharing
   • Interference and prioritization
   • Purpose: Real-world usage simulation

📊 CRITICAL METRICS:

• Latency: Response time (milliseconds)
• Throughput: Data rate (bytes/second)
• Success Rate: Reliability percentage
• Resource Usage: CPU/Memory overhead
• Error Patterns: Timeout/corruption analysis

⚡ PRACTICAL APPLICATIONS:

For robotic hand control:
• Real-time control loops (10-100Hz)
• Tactile sensor data streaming
• Multi-axis coordination
• Safety-critical responsiveness
""")

async def main():
    """Main demo entry point"""
    print_stress_test_concepts()
    
    print("\n🚀 Ready to run interactive demos?")
    response = input("Press Enter to start, or 'q' to quit: ").strip().lower()
    
    if response != 'q':
        await interactive_demo()
    else:
        print("👋 See you next time!")

if __name__ == "__main__":
    print("Communication Throughput Stress Test Demo")
    print("Each test manages its own connections for clean isolation!")
    print("Adjust COM port and IP settings in the code before running!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except ConnectionError as e:
        print(f"\n{e}")
        print("💡 Check your hardware connections and settings!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
