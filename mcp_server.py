from fastmcp import FastMCP

# Instantiate FastMCP server
mcp = FastMCP("Cred-Lending-MCP-Server")

@mcp.tool()
def lookup_loan_application(record_id: str) -> str:
    # Dummy handler for verification
    return f"Application Data for {record_id}"

if __name__ == "__main__":
    # Specify host, port, and transport explicitly
    mcp.run(transport="sse", host="127.0.0.1", port=8000)