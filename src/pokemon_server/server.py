from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl
import asyncio
import json

POKEMON_DATA = {
    "pikachu": {
        "name": "Pikachu",
        "type": "Electric",
        "description": "A Mouse Pokémon. It can generate electric attacks from the electric pouches located in both of its cheeks.",
        "stats": {
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "speed": 90
        }
    }
}

# Create the server
app = Server("pokemon-server")

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available Pokemon resources."""
    return [
        Resource(
            uri=AnyUrl(f"pokemon://{pokemon_id}"),
            name=data["name"],
            mimeType="application/json",
            description=f"Information about {data['name']}"
        )
        for pokemon_id, data in POKEMON_DATA.items()
    ]

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read Pokemon data for a specific Pokemon."""
    pokemon_id = str(uri).replace("pokemon://", "")
    
    if pokemon_id not in POKEMON_DATA:
        raise ValueError(f"Unknown Pokemon: {pokemon_id}")
    
    return json.dumps(POKEMON_DATA[pokemon_id], indent=2)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Pokemon tools."""
    return [

        Tool(
            name="get_stats",
            description="Get detailed stats for a specific Pokemon",
            inputSchema={
                "type": "object",
                "properties": {
                    "pokemon": {
                        "type": "string",
                        "description": "Name of the Pokemon (e.g., pikachu, charizard)",
                    }
                },
                "required": ["pokemon"]
            }
        )
    ]
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Pokemon searches and stats."""
    if name == "get_stats":
        pokemon_name = arguments["pokemon"].lower()
        if pokemon_name not in POKEMON_DATA:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Pokemon {pokemon_name} not found"}, indent=2)
            )]
            
        stats = {
            "name": POKEMON_DATA[pokemon_name]["name"],
            "stats": POKEMON_DATA[pokemon_name]["stats"]
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(stats, indent=2)
        )]
        
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())