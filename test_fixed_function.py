#!/usr/bin/env python3
"""
Test the fixed add_part_to_assembly function
"""

import sys
import asyncio
import logging

# Add FreeCAD path
sys.path.append(r'C:\Program Files\FreeCAD 1.0\bin')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_fixed_function():
    """Test the fixed add_part_to_assembly function"""
    try:
        # Import the function
        from tools.tool_add_part_to_assembly import add_part_to_assembly
        from common_logic import core
        
        print("🧪 Testing the fixed add_part_to_assembly function...")
        
        # Connect to FreeCAD
        connect_result = core.connect()
        if not connect_result["success"]:
            print(f"❌ Failed to connect: {connect_result.get('error', 'Unknown error')}")
            return
        
        print("✅ Connected to FreeCAD")
        
        # Open the document
        open_result = await core.open_document('hehe2.FCStd')
        print(f"✅ Document opened: {open_result}")
        
        # Test adding part - this should now work with the fix
        print("🔧 Testing add_part_to_assembly with assembly_name='hehe2'...")
        result = add_part_to_assembly(core, "hehe2", None, "Box")
        print(f"Result: {result}")
        
        if result.get("success"):
            print("🎉 SUCCESS! Part added to assembly!")
            print(f"   Assembly: {result.get('assembly')}")
            print(f"   Part: {result.get('part')}")
            print(f"   Message: {result.get('message')}")
        else:
            print("❌ FAILED!")
            print(f"   Error: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_function())