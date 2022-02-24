

""" Map between JAWSConsumer and alarm topic
"""
TOPICS = {
   'alarm-registrations'   : { 'consumer_type' : AlarmRegistrationsConsumer,
      'description' : "Topic contains current set of registered alarms" },
   'effective-activations' : { 'consumer_type' :EffectiveActivationsConsumer,
      'description' : "Topic provides an alarm's effective state"},
   'alarm-activations'     : {'consumer_type' : AlarmActivationsConsumer,
      'description' : "Topic provides alarm's actual state"},
   'effective-alarms' : {'consumer_type' : EffectiveAlarmConsumer,
      'description' : ""},
   'alarm-overrides' : { 'consumer_type' : AlarmOverrideConsumer,
      'description' : "Topic containing override information"},
   'alarm-classes' : {'consumer_type' : AlarmClassConsumer,'description': ""},
   'effective-registrations' : {'consumer_type' : EffectiveRegistrationsConsumer,
      'description' : ""}
}




