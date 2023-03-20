"""Tests for the distance calculations."""
import pytest
from matplotlib import pyplot as plt
from numpy import inf

from superblockify.metrics.distances import (
    calculate_distance_matrix,
    calculate_euclidean_distance_matrix_projected,
    calculate_euclidean_distance_matrix_haversine,
    calculate_partitioning_distance_matrix,
)


@pytest.mark.parametrize("weight", ["length", None])
def test_calculate_distance_matrix(test_city_small, weight):
    """Test calculating all pairwise distances for the full graphs."""
    _, graph = test_city_small
    calculate_distance_matrix(graph, weight=weight, plot_distributions=True)
    # With node ordering
    calculate_distance_matrix(
        graph, node_order=list(graph.nodes), plot_distributions=True
    )
    plt.close("all")


def test_calculate_distance_matrix_negative_weight(test_city_small):
    """Test calculating all pairwise distances for the full graphs with negative
    weights.
    """
    _, graph = test_city_small
    # Change the first edge length to -1
    graph.edges[list(graph.edges)[0]]["length"] = -1
    with pytest.raises(ValueError):
        calculate_distance_matrix(graph, weight="length")


def test_calculate_euclidean_distance_matrix_projected(test_city_all):
    """Test calculating all pairwise euclidean distances for the full graphs.
    Projected."""
    _, graph = test_city_all
    calculate_euclidean_distance_matrix_projected(graph, plot_distributions=True)
    # With node ordering
    calculate_euclidean_distance_matrix_projected(
        graph, node_order=list(graph.nodes), plot_distributions=True
    )
    plt.close("all")


@pytest.mark.parametrize(
    "key,value",
    [
        ("x", None),
        ("y", None),
        ("x", "a"),
        ("y", "a"),
        ("x", inf),
        ("y", inf),
        ("x", -inf),
        ("y", -inf),
    ],
)
def test_calculate_euclidean_distance_matrix_projected_faulty_coords(
    test_city_small, key, value
):
    """Test calculating all pairwise euclidean distances for the full graphs
    with missing coordinates. Projected.
    """
    _, graph = test_city_small
    # Change key attribute of first node
    graph.nodes[list(graph.nodes)[0]][key] = value
    with pytest.raises(ValueError):
        calculate_euclidean_distance_matrix_projected(graph)


def test_calculate_euclidean_distance_matrix_projected_unprojected_graph(
    test_city_small,
):
    """Test `calculate_euclidean_distance_matrix_projected` exception handling
    unprojected graph."""
    _, graph = test_city_small

    # Pseudo-unproject graph
    graph.graph["crs"] = "epsg:4326"
    with pytest.raises(ValueError):
        calculate_euclidean_distance_matrix_projected(graph)

    # Delete crs attribute
    graph.graph.pop("crs")
    with pytest.raises(ValueError):
        calculate_euclidean_distance_matrix_projected(graph)


def test_calculate_euclidean_distance_matrix_haversine(test_city_small):
    """Test calculating all pairwise euclidean distances for the full graphs.
    Haversine."""
    _, graph = test_city_small
    calculate_euclidean_distance_matrix_haversine(graph, plot_distributions=True)
    # With node ordering
    calculate_euclidean_distance_matrix_haversine(
        graph, node_order=list(graph.nodes), plot_distributions=True
    )
    plt.close("all")


@pytest.mark.parametrize(
    "key,value",
    [
        ("lat", None),
        ("lon", None),
        ("lat", "a"),
        ("lon", "a"),
        ("lat", -90.1),
        ("lon", -180.1),
        ("lat", 90.1),
        ("lon", 180.1),
        ("lat", inf),
        ("lon", inf),
        ("lat", -inf),
        ("lon", -inf),
    ],
)
def test_calculate_euclidean_distance_matrix_haversine_faulty_coords(
    test_city_small, key, value
):
    """Test calculating all pairwise euclidean distances for the full graphs
    with missing coordinates. Haversine.
    """
    _, graph = test_city_small
    # Change key attribute of first node
    graph.nodes[list(graph.nodes)[0]][key] = value
    with pytest.raises(ValueError):
        calculate_euclidean_distance_matrix_haversine(graph)


@pytest.mark.xfail(reason="Partitioners need to implement `self.sparsified`.")
def test_calculate_partitioning_distance_matrix(test_city_small, partitioner_class):
    """Test calculating distances for partitioned graph by design."""
    city_name, graph = test_city_small
    part = partitioner_class(name=city_name + "_test", city_name=city_name, graph=graph)
    part.run()
    calculate_partitioning_distance_matrix(
        part, plot_distributions=True, check_overlap=True, num_workers=4
    )
    # With node ordering
    calculate_partitioning_distance_matrix(
        part,
        node_order=list(graph.nodes),
        plot_distributions=True,
        check_overlap=True,
        num_workers=4,
    )
    plt.close("all")


@pytest.mark.xfail(reason="Partitioners need to implement `self.sparsified`.")
def test_calculate_partitioning_distance_matrix_partitions_overlap(
    test_city_small, partitioner_class
):
    """Test calculating distances for partitioned graph with overlapping
    partitions."""
    city_name, graph = test_city_small
    part = partitioner_class(name=city_name + "_test", city_name=city_name, graph=graph)
    part.run()
    # Duplicate partitions /component
    if part.components is not None:
        part.components += part.components
    else:
        part.partitions += part.partitions

    with pytest.raises(ValueError):
        calculate_partitioning_distance_matrix(part, check_overlap=True)