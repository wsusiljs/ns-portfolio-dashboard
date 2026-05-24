def filter_data(df, owner_account):

    if owner_account == "ALL":
        return df

    owner, acct = owner_account.split("-")

    return df[
        (df["Owner"] == owner)
        & (df["Account"].str.contains(acct))
    ]
