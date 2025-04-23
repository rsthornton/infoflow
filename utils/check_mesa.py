#!/usr/bin/env python3.11
"""
Check Mesa installation details.
"""

import mesa
import sys
import inspect
import importlib.metadata

print(f"Python version: {sys.version}")
print(f"Mesa version: {mesa.__version__}")
print(f"Mesa location: {mesa.__file__}")

# Try to import key Mesa 3 features using correct paths from the guide
print("\nChecking for Mesa 3 features:")
try:
    from mesa.agent import AgentSet
    print("✓ AgentSet is available from mesa.agent")
except ImportError:
    print("✗ AgentSet is NOT available from mesa.agent")

try:
    # Check if Agent class has create_agents as a class method
    if hasattr(mesa.Agent, 'create_agents'):
        print("✓ create_agents method is available on mesa.Agent")
    else:
        print("✗ create_agents method is NOT available on mesa.Agent")
except Exception as e:
    print(f"✗ Error checking mesa.Agent: {e}")

# List all Mesa modules imported
print("\nAll Mesa modules imported:")
for name, module in inspect.getmembers(mesa, inspect.ismodule):
    print(f"- {name}")

# Try to create a minimal test model
print("\nTesting minimal model:")
try:
    class TestAgent(mesa.Agent):
        def __init__(self, model):
            super().__init__(model)
            self.x = 1
            
        def step(self):
            self.x += 1
            
    class TestModel(mesa.Model):
        def __init__(self, n=5):
            super().__init__()
            # Try creating agents using both approaches
            try:
                TestAgent.create_agents(model=self, n=n)
                print("✓ Successfully created agents with create_agents")
            except Exception as e:
                print(f"✗ Failed to create agents: {e}")
                
                # Fallback to manual creation
                print("  Falling back to manual agent creation")
                for i in range(n):
                    agent = TestAgent(self)
                    
            # Check model properties
            print(f"✓ Model has agents property: {hasattr(self, 'agents')}")
            if hasattr(self, 'agents'):
                print(f"✓ Number of agents: {len(self.agents)}")
                print(f"  Agent methods: {dir(self.agents)[:5]}...")

    # Create and test model
    model = TestModel()
except Exception as e:
    print(f"✗ Error testing model: {e}")