"""Conditional form fields: fields gated by a switch (e.g. ``sourceType``).

Update forms (e.g. ``compose.update``, ``application.update``) expose every
provider-specific field at once. This curated map groups those fields by the
value of a switch field, so the form can hide the groups that do not apply
(e.g. ``sourceType=raw`` hides the github/bitbucket/gitlab/gitea fields).

Each entity spec is ``{"switches": [{"switch": field, "groups": {value: [fields]}}]}``.
Fields not listed in any group are always visible ("common"). A blank switch
value shows the common fields only.
"""

CONDITIONAL_FIELDS: dict[str, dict] = {
    "compose": {
        "switches": [
            {
                "switch": "sourceType",
                "groups": {
                    "github": ["githubId", "branch", "owner", "repository", "composePath"],
                    "gitlab": [
                        "gitlabId",
                        "gitlabBranch",
                        "gitlabOwner",
                        "gitlabPathNamespace",
                        "gitlabProjectId",
                        "gitlabRepository",
                        "composePath",
                    ],
                    "bitbucket": [
                        "bitbucketId",
                        "bitbucketBranch",
                        "bitbucketOwner",
                        "bitbucketRepository",
                        "bitbucketRepositorySlug",
                        "composePath",
                    ],
                    "gitea": ["giteaId", "giteaBranch", "giteaOwner", "giteaRepository", "composePath"],
                    "git": ["customGitUrl", "customGitBranch", "customGitSSHKeyId", "composePath"],
                    "raw": ["composeFile"],
                },
            },
        ],
    },
    "application": {
        "switches": [
            {
                "switch": "sourceType",
                "groups": {
                    "github": ["githubId", "branch", "owner", "repository"],
                    "gitlab": [
                        "gitlabId",
                        "gitlabBranch",
                        "gitlabOwner",
                        "gitlabPathNamespace",
                        "gitlabProjectId",
                        "gitlabRepository",
                        "gitlabBuildPath",
                    ],
                    "bitbucket": [
                        "bitbucketId",
                        "bitbucketBranch",
                        "bitbucketOwner",
                        "bitbucketRepository",
                        "bitbucketRepositorySlug",
                        "bitbucketBuildPath",
                    ],
                    "gitea": ["giteaId", "giteaBranch", "giteaOwner", "giteaRepository", "giteaBuildPath"],
                    "git": ["customGitUrl", "customGitBranch", "customGitSSHKeyId", "customGitBuildPath"],
                    "docker": ["dockerImage", "registryId", "registryUrl", "username", "password"],
                    "drop": ["dropBuildPath"],
                },
            },
            {
                "switch": "buildType",
                "groups": {
                    "dockerfile": ["dockerfile", "dockerContextPath", "dockerBuildStage"],
                    "heroku_buildpacks": ["herokuVersion"],
                    "static": ["publishDirectory", "isStaticSpa"],
                    "railpack": ["railpackVersion"],
                },
            },
        ],
    },
}


def conditional_switches(entity: str) -> list[dict]:
    """The switch specs for an entity's forms, if curated."""
    return CONDITIONAL_FIELDS.get(entity, {}).get("switches", [])
