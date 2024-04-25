from gymnasium.envs.registration import register

register(id='VSS-v0',
         entry_point='rsoccer_gym.vss.env_vss:VSSEnv',
         )

register(id='VSSMA-v0',
         entry_point='rsoccer_gym.vss.env_ma:VSSMAEnv',
         )

register(id='VSSMAOpp-v0',
         entry_point='rsoccer_gym.vss.env_ma:VSSMAOpp',
         )

register(id='VSSGk-v0',
         entry_point='rsoccer_gym.vss.env_gk:rSimVSSGK',
         )

register(id='VSSFIRA-v0',
         entry_point='rsoccer_gym.vss.env_vss:VSSEnv',
         kwargs={'use_fira': True},
         )
