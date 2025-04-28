#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Coder:Whitejoce

import inspect, json
from fastmcp import FastMCP

mcp = FastMCP("Demo", debug=True, log_level="DEBUG")

'''
@mcp.tool()
def add(a: int,b: int)-> int:
    """Add two numbers"""
    return a+b
'''


def load_tools():
    '''Loads tools defined in tools.json'''
    try:
        with open("tools.json", "r", encoding="utf-8") as f:
            tools_data = json.load(f)
    except FileNotFoundError:
        print("Error: tools.json not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding tools.json: {e}")
        return

    for tool in tools_data:
        tool_name = tool.get("name")
        tool_code = tool.get("code")
        tool_description = tool.get("description")

        # Validate essential tool information
        if not tool_name or not isinstance(tool_name, str):
            print(f"Warning: Skipping tool due to missing or invalid 'name'. Tool data: {tool}")
            continue
        if not tool_code or not isinstance(tool_code, str):
            print(f"Warning: Skipping tool '{tool_name}' due to missing or invalid 'code'.")
            continue
        if not tool_description or not isinstance(tool_description, str):
             print(f"Warning: Skipping tool '{tool_name}' due to missing or invalid 'description'.")
             continue

        print(
            f"Loading tool: {tool_name}, Code: {tool_code[:50]}..."
        )
        local_namespace = {}
        ## Execute the tool's code within a local namespace
        try:
            # [!] This code may be unsafe if the tool code is not trusted
            exec(tool_code, globals(), local_namespace)

            # Find the function defined in the code
            found_func = None
            for _, obj in local_namespace.items():
                # Check if it's a function defined in the executed code's namespace
                if inspect.isfunction(obj) and obj.__name__ in local_namespace:
                    if found_func is not None:
                         # Handle case where multiple functions are defined if necessary
                         print(f"Warning: Multiple functions found for tool '{tool_name}'. Using the first one found ('{found_func.__name__}').")
                         # Optionally raise an error here instead of just warning
                         break # Keep the first one found as per original logic
                    found_func = obj
                    print(
                        f"Found function '{obj.__name__}' in executed code for tool '{tool_name}'"
                    )
                    # Don't break immediately if we want to check for multiple functions explicitly

            if found_func:
                # Add the tool to MCP using the database name
                mcp.tool(
                    name=tool_name, description=tool_description
                )(found_func)
                print(f"Successfully registered tool '{tool_name}'")
            else:
                print(
                    f"Warning: No function found in code for tool '{tool_name}'"
                )
        except Exception as e:
            print(f"Error loading tool '{tool_name}': {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging


if __name__ == "__main__":
    load_tools()
    mcp.run(transport="sse")
