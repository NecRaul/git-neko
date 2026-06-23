def matches_access(repo, username, orgs, option):
    if "all" in option:
        return True

    owner = repo.get("owner", {})
    owner_login = owner.get("login")
    owner_type = owner.get("type")
    permissions = repo.get("permissions", {})

    if "owner" in option and owner_login == username:
        return True
    if "collaborator" in option and owner_login != username and permissions.get("push"):
        return True

    if "accessible" in option and owner_login != username and permissions.get("pull"):
        return True

    if "org-member" in option and owner_login in orgs and owner_type == "Organization":
        return True

    return False


def matches_visibility(repo, option):
    if "all" in option:
        return True
    return repo["visibility"] in option


def matches_fork(repo, option):
    return matches_bool(repo["fork"], option)


def matches_archived(repo, option):
    return matches_bool(repo["archived"], option)


def matches_template(repo, option):
    return matches_bool(repo["is_template"], option)


def matches_bool(value, option):
    if option == "both":
        return True
    return value == (option == "yes")
