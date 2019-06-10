import opengnn as ognn


def subtokenizer(token):
    no_snake_case = token.split('_')
    subtokens = []
    for su in no_snake_case:
        subtokens += re.sub('([A-Z][a-z]+)', r' \1',
                            re.sub('([A-Z]+)', r' \1', su)).split()
    return subtokens


def model():
    return ognn.models.GraphRegressor(
        source_inputter=ognn.inputters.token_embedder.SubtokenEmbedder(
            subtokenizer=subtokenizer,
            vocabulary_file_key="node_vocabulary",
            embedding_size=65536),
        target_inputter=ognn.inputters.token_embedder.SubtokenEmbedder(
            subtokenizer=subtokenizer,
            vocabulary_file_key="type_vocabulary",
            embedding_size=2048),
        encoder=ognn.encoders.GGNNEncoder(
            num_timesteps=[2, 2],
            node_feature_size=65536),
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
