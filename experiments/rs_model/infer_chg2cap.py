"""Chg2Cap 独立推理脚本：加载训练好的权重，对“新的”遥感影像对生成变化描述。

重要：本脚本要放在 **Chg2Cap 仓库根目录** 下运行（用到它自带的 model/ 模块）。
示例（在 4060 机器上）：

    # 单对影像
    python infer_chg2cap.py --imgA /path/before.png --imgB /path/after.png

    # 批量：目录里有 A/ 和 B/ 两个子文件夹，文件名一一对应
    python infer_chg2cap.py --pairs_dir ./my_pairs --out captions.json

说明：
- 输入会缩放到 256x256（LEVIR-CC 训练尺寸）。
- 归一化参数与训练一致（取自 data/LEVIR_CC/LEVIRCC.py）：
      mean = [100.6790, 99.5023, 84.9932]
      std  = [50.9820, 48.4838, 44.7057]
- 生成的 caption 是英文（LEVIR-CC 标注为英文）。
- 需要 CUDA（模型内部写死了 .cuda()）。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from model.model_encoder import AttentiveEncoder, Encoder
from model.model_decoder import DecoderTransformer

MEAN = [100.6790, 99.5023, 84.9932]
STD = [50.9820, 48.4838, 44.7057]
SPECIALS = {"<START>", "<END>", "<NULL>"}


def load_vocab(vocab_path: str) -> dict:
    with open(vocab_path, "r") as f:
        return json.load(f)


def build_and_load(args, word_vocab):
    encoder = Encoder(args.network)
    encoder_trans = AttentiveEncoder(
        n_layers=args.n_layers,
        feature_size=[args.feat_size, args.feat_size, args.encoder_dim],
        heads=args.n_heads,
        hidden_dim=args.hidden_dim,
        attention_dim=args.attention_dim,
        dropout=args.dropout,
    )
    decoder = DecoderTransformer(
        encoder_dim=args.encoder_dim,
        feature_dim=args.feature_dim,
        vocab_size=len(word_vocab),
        max_lengths=args.max_length,
        word_vocab=word_vocab,
        n_head=args.n_heads,
        n_layers=args.decoder_n_layers,
        dropout=args.dropout,
    )

    ckpt = torch.load(args.checkpoint, map_location="cpu")
    encoder.load_state_dict(ckpt["encoder_dict"])
    encoder_trans.load_state_dict(ckpt["encoder_trans_dict"])
    decoder.load_state_dict(ckpt["decoder_dict"])

    encoder.eval().cuda()
    encoder_trans.eval().cuda()
    decoder.eval().cuda()
    return encoder, encoder_trans, decoder


def preprocess(path: str, size: int) -> torch.Tensor:
    img = Image.open(path).convert("RGB").resize((size, size))
    arr = np.asarray(img, np.float32)  # HWC
    arr = np.moveaxis(arr, -1, 0)  # CHW
    for i in range(3):
        arr[i] = (arr[i] - MEAN[i]) / STD[i]
    return torch.from_numpy(arr).unsqueeze(0)


def tokens_to_caption(seq, word_vocab: dict) -> str:
    words = list(word_vocab.keys())
    out = []
    for idx in seq:
        w = words[int(idx)]
        if w in SPECIALS:
            continue
        out.append(w)
    return " ".join(out).strip()


@torch.no_grad()
def predict(encoder, encoder_trans, decoder, word_vocab, path_a, path_b, size) -> str:
    a = preprocess(path_a, size).cuda()
    b = preprocess(path_b, size).cuda()
    f1, f2 = encoder(a, b)
    f1, f2 = encoder_trans(f1, f2)
    seq = decoder.sample(f1, f2)
    return tokens_to_caption(seq, word_vocab)


def collect_pairs(pairs_dir: str):
    adir = Path(pairs_dir) / "A"
    bdir = Path(pairs_dir) / "B"
    if not adir.is_dir() or not bdir.is_dir():
        raise SystemExit(f"目录里需要有 A/ 和 B/ 子文件夹：{pairs_dir}")
    pairs = []
    for a in sorted(adir.iterdir()):
        if a.is_file():
            b = bdir / a.name
            if b.exists():
                pairs.append((str(a), str(b)))
            else:
                print(f"[跳过] B/ 里没有同名文件：{a.name}")
    return pairs


def main() -> None:
    p = argparse.ArgumentParser(description="Chg2Cap inference on new image pairs")
    p.add_argument("--checkpoint", default="./models_checkpoint/LEVIR_CC_batchsize_32_resnet101.pth")
    p.add_argument("--vocab", default="./data/LEVIR_CC/vocab.json")
    p.add_argument("--network", default="resnet101")
    p.add_argument("--size", type=int, default=256, help="输入缩放尺寸（LEVIR-CC 为 256）")

    p.add_argument("--imgA", default=None, help="单对推理：变化前影像")
    p.add_argument("--imgB", default=None, help="单对推理：变化后影像")
    p.add_argument("--pairs_dir", default=None, help="批量推理：含 A/ 与 B/ 的目录")
    p.add_argument("--out", default="captions.json", help="批量时输出 JSON 路径")

    # 模型结构参数（与 test.py 保持一致）
    p.add_argument("--encoder_dim", type=int, default=2048)
    p.add_argument("--feat_size", type=int, default=16)
    p.add_argument("--n_heads", type=int, default=8)
    p.add_argument("--n_layers", type=int, default=3)
    p.add_argument("--decoder_n_layers", type=int, default=1)
    p.add_argument("--hidden_dim", type=int, default=512)
    p.add_argument("--attention_dim", type=int, default=2048)
    p.add_argument("--feature_dim", type=int, default=2048)
    p.add_argument("--dropout", type=float, default=0.1)
    p.add_argument("--max_length", type=int, default=41)
    p.add_argument("--gpu_id", type=int, default=0)
    args = p.parse_args()

    import os

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)

    word_vocab = load_vocab(args.vocab)
    print(f"vocab 大小：{len(word_vocab)}；checkpoint：{args.checkpoint}")
    encoder, encoder_trans, decoder = build_and_load(args, word_vocab)
    print("模型加载完成，开始推理。")

    if args.imgA and args.imgB:
        cap = predict(encoder, encoder_trans, decoder, word_vocab, args.imgA, args.imgB, args.size)
        print("\n=== 变化描述 ===")
        print(cap)
        return

    if args.pairs_dir:
        pairs = collect_pairs(args.pairs_dir)
        print(f"共 {len(pairs)} 对影像。")
        results = []
        for i, (pa, pb) in enumerate(pairs, 1):
            cap = predict(encoder, encoder_trans, decoder, word_vocab, pa, pb, args.size)
            print(f"[{i}/{len(pairs)}] {Path(pa).name}: {cap}")
            results.append({"A": pa, "B": pb, "caption": cap})
        Path(args.out).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n已写出：{args.out}")
        return

    raise SystemExit("请提供 --imgA/--imgB（单对）或 --pairs_dir（批量）。")


if __name__ == "__main__":
    main()
