import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    # Append /sse to establish the SSE stream connection
    server_url = "http://127.0.0.1:8000/sse"  # or "http://127.0.0.1:8000/mcp/sse"
    print(f"Connecting standalone MCP Client to {server_url}...")
    
    test_ids = ["CRD-LN-1001", "CRD-LN-1002"]
    
    try:
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("MCP Session successfully initialized.")
                
                for rid in test_ids:
                    print(f"\n--- Invoking MCP Tool 'lookup_loan_application' for Record ID: {rid} ---")
                    result = await session.call_tool(
                        name="lookup_loan_application",
                        arguments={"record_id": rid}
                    )
                    
                    mcp_formatted_response = {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [
                                {
                                    "type": content.type,
                                    "text": content.text
                                }
                                for content in result.content
                            ]
                        },
                        "id": 1
                    }
                    print("Standardized MCP Server Output:")
                    print(json.dumps(mcp_formatted_response, indent=2))
                    
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())