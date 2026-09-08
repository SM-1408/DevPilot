# TODO: improve authentication


def process_user(
    name,
    email,
    age,
    city,
    country,
    phone,
    role
):

    if name:

        if email:

            if age > 18:

                if role == "admin":
                    return "Admin"

    return "User"