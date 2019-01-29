from belief_propagation_ure import *

rain = ConceptNode('Rain')
wet_grass = ConceptNode('WetGrass')
wet_grass_given_rain = ImplicationLink(rain, wet_grass)

rain.set_value(CDV_KEY, FloatValue([0.2, 0.8]))
rain.set_value(SHAPE_KEY, FloatValue(2))
wet_grass.set_value(SHAPE_KEY, FloatValue(2))
wet_grass_given_rain.set_value(CDV_KEY, FloatValue([0.9, 0.1, 0.25, 0.75]))

init_factor_graph()

send_messages()

# show_values(rain, 'Rain')
# show_values(ConceptNode("Factor-Rain"), 'Factor Rain')

# show_atomspace()
