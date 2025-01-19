"""
app/utils/amulet_merge.py

Contains helper functions for merging worlds using Amulet.
"""

from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist

def merge_amulet_worlds(uploaded_world, local_world):
    """
    Overwrites local chunks with the uploaded chunks (unconditionally).
    """
    for dimension in uploaded_world.dimensions:
        if dimension not in local_world.dimensions:
            local_world.create_dimension(dimension)
        coords = list(uploaded_world.all_chunk_coords(dimension))
        for (cx, cz) in coords:
            try:
                uploaded_chunk = uploaded_world.get_chunk(cx, cz, dimension)
            except (ChunkLoadError, ChunkDoesNotExist):
                continue
            if not is_chunk_empty(uploaded_chunk):
                local_world.put_chunk(uploaded_chunk, dimension)

def is_chunk_empty(chunk):
    """Basic check if chunk is 'empty' (no block data)."""
    if chunk is None:
        return True
    if not hasattr(chunk, 'blocks') or chunk.blocks is None:
        return True
    return False
