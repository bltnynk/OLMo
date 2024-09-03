import json

import matplotlib.pyplot as plt
import numpy as np

from olmo.scaling.scaling_laws.utils import (
    ExtrapolateNConfig,
    get_ax,
    get_coefficients_huber,
    get_data_by_name,
    grad_tissue_fit,
    parse_args,
    tissue_fit,
)


def main():
    args = parse_args()

    with open(args.config_path) as f:
        configs = json.load(f)
        configs = {name: ExtrapolateNConfig(**config) for name, config in configs.items()}

    data_by_name = get_data_by_name(configs, args.keys, min_step=3000)

    num_axs = 5
    fig, axs = plt.subplots(1, num_axs, figsize=(num_axs * 8, 6))

    train_ns1s2s, train_ys = [], []
    for name, data in data_by_name.items():
        config = configs[name]
        if config.mode == "train":
            train_ns1s2s += [[n, s1, s2] for n, s1, s2 in zip(data["ns"], data["s1s"], data["s2s"])]
            train_ys += data["ys"]

    # fit the parameters
    coefficients = get_coefficients_huber(
        train_ns1s2s,
        train_ys,
        tissue_fit,
        grad_tissue_fit,
        p0=[4.0, 4.0, 0.25, 0.7, 1.5, 0.01, 0.01],
        bounds=[(None, None), (None, None), (0, None), (0, None), (0, None), (0, None), (0, None)],
    )
    a, b, alpha, beta, E, F, gamma = coefficients
    A, B = np.exp(a), np.exp(b)

    # make predictions
    predicted_data_by_name = {}
    for name, data in data_by_name.items():
        config = configs[name]
        predicted_data_by_name[name] = {
            "ds": data["ds"],
            "s1s": data["s1s"],
            "s2s": data["s2s"],
            "ys": [
                tissue_fit([n, s1, s2], coefficients) for n, s1, s2 in zip(data["ns"], data["s1s"], data["s2s"])
            ],
        }

    # plot the actual data
    for name, data in data_by_name.items():
        config = configs[name]
        ax = axs[get_ax(name)]
        ax.scatter(data["ds"], data["ys"], color="white", edgecolors=config.color, label=config.label, s=5.0)

    # plot the fitted curve
    for name, data in predicted_data_by_name.items():
        config = configs[name]
        ax = axs[get_ax(name)]
        if config.mode == "train":
            ax.plot(
                data["ds"],
                data["ys"],
                color=config.color,
                linestyle="--",
                linewidth=0.8,
                label=f"{config.label} (fitted)",
            )
        else:
            ax.plot(
                data["ds"],
                data["ys"],
                color=config.color,
                linestyle="--",
                linewidth=0.8,
                label=f"{config.label} (predicted)",
            )
    plt.text(
        x=0.40,
        y=0.90,
        s=f"L(n, s1, s2) = {A:.2f} / n^{alpha:.2f} + {B:.2f} / s1^{beta:.2f} + {E:.2f} - {F:.2f} * s2 * n^{gamma:.2f}",
        fontsize=12,
        transform=fig.transFigure,
    )

    for ax in axs:
        ax.legend(loc="upper right", ncols=2, fontsize=10)
        ax.set_xlabel("Tokens (d)")
    axs[0].set_ylabel(f"CE loss, {args.key if args.key != '' else args.keys}")
    plt.suptitle("Fitting loss curves, with Tissue function")
    plt.savefig(args.output_path, dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
