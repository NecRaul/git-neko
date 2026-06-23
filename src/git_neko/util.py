def matches_access(repo, username, orgs, filter):
    if "all" in filter:
        return True

    owner = repo.get("owner", {})
    owner_login = owner.get("login")
    owner_type = owner.get("type")
    permissions = repo.get("permissions", {})

    if "owner" in filter and owner_login == username:
        return True
    if "collaborator" in filter and owner_login != username and permissions.get("push"):
        return True

    if "accessible" in filter and owner_login != username and permissions.get("pull"):
        return True

    if "org-member" in filter and owner_login in orgs and owner_type == "Organization":
        return True

    return False


def matches_visibility(repo, filter):
    if "all" in filter:
        return True
    return repo["visibility"] in filter


def matches_fork(repo, filter):
    return matches_bool(repo["fork"], filter)


def matches_archived(repo, filter):
    return matches_bool(repo["archived"], filter)


def matches_template(repo, filter):
    return matches_bool(repo["is_template"], filter)


def matches_bool(value, filter):
    if filter == "both":
        return True
    return value == (filter == "yes")


def remove_none(data):
    if isinstance(data, dict):
        return {
            key: remove_none(value) for key, value in data.items() if value is not None
        }
    return data
