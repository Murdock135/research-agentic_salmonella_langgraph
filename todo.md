# Refactor code

1. create `src/sparq/` directory
2. move all sub-modules of `sparq/` into `src/sparq/`
3. Update `pyproject.toml`
4. Install package locally with `pip install -e .`
5. Update all import statements accordingly

# Refactoring stage 2
1. Move `config` into a separete directory outside `sparq/`
2. Separate helper functions and move appropriate functions to other places; 
    - helper functions that help sparq
    - helper functions that help other modules like config, experiments, etc.