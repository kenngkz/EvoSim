# Planning

## Gene representation
1. connection - (from_node, to_node, weight)
2. node - (node_id, status): status represents whether node is active or not
3. attr - ? : make this expandable to add new attr in the future
    - speed
    - vision range
    - type of food digestion
    - size

## Podd observation space


## How to do NN calculations
1. numpy/tensorflow will not be the best for dynamic connections architecture.
2. with manual calculation, will be very slow (i think)
    - can speed it up with numba?