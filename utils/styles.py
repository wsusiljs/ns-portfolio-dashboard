def style_fig(fig, height=500):

    fig.update_layout(
        height=height,
        margin=dict(
            l=10,
            r=10,
            t=40,
            b=10
        ),
        legend=dict(
            orientation="h",
            y=-0.2
        )
    )

    return fig
