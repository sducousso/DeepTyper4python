ognn-build-vocab --field_name node_labels --save_vocab node.vocab ._graphs_mock_train.jsonl

ognn-build-vocab --no_pad_token --field_name edges --string_index 0 --save_vocab edge.vocab ._graphs_mock.jsonl

ognn-build-vocab --no_pad_token --field_name annotation_type --string_index 1 --save_vocab type.vocab data/.graph_simple.jsonl

ognn-main train_and_eval --model model_ggnn.py --config config.yml