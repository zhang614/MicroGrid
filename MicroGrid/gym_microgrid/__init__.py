from gym.envs.registration import register

register(
    id='MicroGrid-v0',
    entry_point='gym_microgrid.microgrid:MicroGrid',
)