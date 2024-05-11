from gymnasium.envs.registration import register

register(id='VSSMA-v0',
         entry_point='rsoccer_gym.vss.env_ma:VSSMAEnv',
         )

register(id='VSSMAOpp-v0',
         entry_point='rsoccer_gym.vss.env_ma:VSSMAOpp',
         )

register(id='VSS1vs1-v0',
         entry_point='rsoccer_gym.vss.env_1vs1:VSS1vs1Env',
        )