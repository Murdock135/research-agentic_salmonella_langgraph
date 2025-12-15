# Refactor code

# Refactoring stage 2
1. Move `config` into a separete directory outside `sparq/`
2. Remove all code's dependence on `config` module inside `sparq/` and make them dependent on `settings` module inside `sparq/` instead.
2. Separate helper functions and move appropriate functions to other places; 
    - helper functions that help sparq
    - helper functions that help other modules like config, experiments, etc.