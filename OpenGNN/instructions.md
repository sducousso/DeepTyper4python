## To execute
```
cd data/pcode
```

If the vocabulary are not build:
```
ognn-build-vocab --field_name node_labels --save_vocab node.vocab data/._graphs_mock_train.jsonl

ognn-build-vocab --no_pad_token --field_name edges --string_index 0 --save_vocab edge.vocab data/._graphs_mock_train.jsonl

ognn-build-vocab --no_pad_token --field_name annotation_type --string_index 1 --save_vocab type.vocab data/._graphs_mock_train.jsonl
```

To launch the network:
```
ognn-main train_and_eval --model model_ggnn.py --config config.yml
```