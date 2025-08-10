#!/usr/bin/env python3
"""
GED Document Management System Launcher
Starts all components of the improved GED system
"""

import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread
import signal

class GEDSystemLauncher:
    def __init__(self):
        self.processes = {}
        self.ports = {
            "main_app": 8502,
            "analytics": 8503,
            "api": 8000
        }
        self.urls = {
            "main_app": "http://localhost:8502",
            "analytics": "http://localhost:8503",
            "api": "http://localhost:8000"
        }
    
    def start_component(self, name, command, port):
        """Start a component in a separate thread"""
        try:
            print(f"🚀 Starting {name} on port {port}...")
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes[name] = process
            
            # Wait a bit for the process to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {name} started successfully on port {port}")
                return True
            else:
                print(f"❌ {name} failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {name}: {e}")
            return False
    
    def start_all_components(self):
        """Start all components of the GED system"""
        print("🏢 GED Document Management System Launcher")
        print("=" * 50)
        
        # Start components
        components = [
            ("main_app", f"streamlit run interface/enhanced_app.py --server.port {self.ports['main_app']}", self.ports['main_app']),
            ("analytics", f"streamlit run improvements/simple_dashboard.py --server.port {self.ports['analytics']}", self.ports['analytics']),
            ("api", f"python improvements/api_server.py", self.ports['api'])
        ]
        
        started_components = []
        
        for name, command, port in components:
            if self.start_component(name, command, port):
                started_components.append(name)
        
        if started_components:
            print(f"\n🎉 Successfully started {len(started_components)} components!")
            self.show_navigation_menu()
        else:
            print("❌ No components started successfully")
            return False
        
        return True
    
    def show_navigation_menu(self):
        """Show navigation menu with links to all components"""
        print("\n" + "=" * 50)
        print("🧭 NAVIGATION MENU")
        print("=" * 50)
        
        menu_items = [
            ("📄 Document Classifier", self.urls["main_app"]),
            ("📊 Analytics Dashboard", self.urls["analytics"]),
            ("🔍 API Health Check", f"{self.urls['api']}/health")
        ]
        
        for i, (name, url) in enumerate(menu_items, 1):
            print(f"{i}. {name}: {url}")
        
        print("\n💡 Tips:")
        print("- Use the navigation sidebar in each app to switch between components")
        print("- The API provides REST endpoints for integration")
        print("- Analytics dashboard shows real-time processing statistics")
        print("- Press Ctrl+C to stop all components")
        
        # Try to open main app in browser
        try:
            print(f"\n🌐 Opening main app in browser...")
            webbrowser.open(self.urls["main_app"])
        except:
            print("⚠️  Could not open browser automatically")
    
    def stop_all_components(self):
        """Stop all running components"""
        print("\n🛑 Stopping all components...")
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except:
                try:
                    process.kill()
                    print(f"🔨 {name} force killed")
                except:
                    print(f"❌ Could not stop {name}")
        
        print("👋 GED system shutdown complete")
    
    def run(self):
        """Run the launcher"""
        try:
            if self.start_all_components():
                print("\n⏳ System is running. Press Ctrl+C to stop...")
                
                # Keep the main thread alive
                while True:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            self.stop_all_components()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.stop_all_components()

def main():
    """Main function"""
    launcher = GEDSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
