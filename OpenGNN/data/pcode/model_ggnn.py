import opengnn as ognn
from opengnn.models.graph_to_annotation import GraphToAnnotation
from opengnn.inputters.is_int_inputter import IsIntInputter


# def subtokenizer(token):
#     no_snake_case = token.split('_')
#     subtokens = []
#     for su in no_snake_case:
#         subtokens += re.sub('([A-Z][a-z]+)', r' \1',
#                             re.sub('([A-Z]+)', r' \1', su)).split()
#     return subtokens


def model():
    return GraphToAnnotation(
        source_inputter=ognn.inputters.TokenEmbedder(
            vocabulary_file_key="node_vocabulary",
            embedding_size=16),  # Size of hidden vectors
        target_inputter=IsIntInputter(),
        encoder=ognn.encoders.GGNNEncoder(
            num_timesteps=[2, 2],
            node_feature_size=16),
        decoder=ognn.decoders.sequence.RNNDecoder(
            num_units=16,
            num_layers=1),
        name="pythonAnnotationModel")

    # return ognn.models.GraphRegressor(
    #     source_inputter=ognn.inputters.token_embedder.SubtokenEmbedder(
    #         subtokenizer=subtokenizer,
    #         vocabulary_file_key="node_vocabulary",
    #         embedding_size=512),
    #     target_inputter=ognn.inputters.TokenEmbedder(
    #         vocabulary_file_key="type_vocabulary",
    #         embedding_size=156
    #     ),
    #     encoder=ognn.encoders.GGNNEncoder(
    #         num_timesteps=[2, 2],
    #         node_feature_size=512),
    #     name="pythonAnnotationModel")
