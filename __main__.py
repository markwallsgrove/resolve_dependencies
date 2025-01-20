from poetry.core.constraints.version import parse_constraint
from poetry.core.constraints.version.version import Version


# Define available versions for each service
def resolve_versions(services, available_versions):
    constraints = {}

    # Aggregate constraints for each service
    for service, dependencies in services.items():
        for dep, constraint in dependencies.items():
            if dep not in constraints:
                constraints[dep] = []
            constraints[dep].append(parse_constraint(constraint))

    resolved_versions = {}

    # Resolve each service version
    for service, service_constraints in constraints.items():
        compatible_versions = []
        for version in available_versions.get(service, []):
            parsed_version = Version.parse(version)
            if all(constraint.allows(parsed_version) for constraint in service_constraints):
                compatible_versions.append(version)
        
        if not compatible_versions:
            raise ValueError(f"Cannot resolve version for {service}")
        
        resolved_versions[service] = max(compatible_versions, key=Version.parse)

    return resolved_versions


if __name__ == "__main__":
    available_versions = {
        "service_y": ["1.2.3", "1.5.0", "1.5.1"],
        "service_z": ["1.4.0", "1.4.1", "1.5.0"],
    }

    # resolves correctly
    resolved_versions = resolve_versions(
        {
            "service_x": {"service_y": "1.2.3", "service_z": "1.4.*"},
            "service_y": {"service_z": "1.4.1"},
        },
        available_versions
    )
    print(f"Resolved versions: {resolved_versions}")

    # conflict on service z requirements
    try:
        resolve_versions(
            {
                "service_x": {"service_y": "1.2.3", "service_z": "1.4.*"},
                "service_y": {"service_z": "1.5.*"},
            },
            available_versions
        )
    except ValueError as e:
        print(e)
