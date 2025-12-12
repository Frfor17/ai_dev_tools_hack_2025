#!/usr/bin/env python3
"""
Test script to diagnose the assembly issue
"""

import sys
import os
import logging

# Add FreeCAD path
sys.path.append(r'C:\Program Files\FreeCAD 1.0\bin')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_assembly_diagnosis():
    """Test the assembly diagnosis"""
    try:
        import FreeCAD
        print("✅ FreeCAD imported successfully")
        
        # Open the hehe2.FCStd file
        doc = FreeCAD.openDocument('hehe2.FCStd')
        print(f"✅ Document opened: {doc.Name}")
        
        # List all objects
        print("\n📋 All objects in document:")
        for obj in doc.Objects:
            print(f"  - {obj.Name} (Type: {obj.TypeId}, Label: {obj.Label})")
        
        # Check for Assembly object
        assembly = doc.getObject('Assembly')
        if assembly:
            print(f"\n✅ Found Assembly object:")
            print(f"  Name: {assembly.Name}")
            print(f"  TypeId: {assembly.TypeId}")
            print(f"  Label: {assembly.Label}")
            if hasattr(assembly, 'Group'):
                print(f"  Children: {[child.Name for child in assembly.Group]}")
        else:
            print("\n❌ No Assembly object found")
        
        # Check for hehe2 object
        hehe2_obj = doc.getObject('hehe2')
        if hehe2_obj:
            print(f"\n✅ Found hehe2 object:")
            print(f"  Name: {hehe2_obj.Name}")
            print(f"  TypeId: {hehe2_obj.TypeId}")
            print(f"  Label: {hehe2_obj.Label}")
        else:
            print("\n❌ No hehe2 object found")
            
        # Test the add_part_to_assembly function
        print("\n🧪 Testing add_part_to_assembly function...")
        
        # Import the function
        from tools.tool_add_part_to_assembly import add_part_to_assembly
        from common_logic import core
        
        # Connect to FreeCAD
        connect_result = core.connect()
        if not connect_result["success"]:
            print(f"❌ Failed to connect: {connect_result.get('error', 'Unknown error')}")
            return
        
        # Open the document
        open_result = core.open_document('hehe2.FCStd')
        print(f"Document open result: {open_result}")
        
        # Test adding part
        result = add_part_to_assembly(core, "hehe2", None, "Box")
        print(f"Add part result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_assembly_diagnosis()