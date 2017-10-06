#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include "graph.h"
#include "tsp_algo_nearest_neighbors.h"

namespace py = pybind11;


PYBIND11_MAKE_OPAQUE(std::vector<int>);

Graph* g_graph = new Graph();

void addVertex(int id, int x, int y) {
    g_graph->addVertex(id, x, y);
}

void resetGraph() {
    delete g_graph;
    g_graph = new Graph();
}

std::vector<int> getNNRoute() {
    if (g_graph->getNumVertices() > 0) {
      TSP_Algos::TSP_Algo_Nearest_Neighbors algo_nn(g_graph);
      algo_nn.findPath();
      std::vector<int> vec_path = algo_nn.getRoute();
      return vec_path;
    }
    return std::vector<int>();
}

std::vector<int> getTwoOptRoute() {
    if (g_graph->getNumVertices() > 0) {
      TSP_Algos::TSP_Algo_Nearest_Neighbors algo_nn(g_graph);
      algo_nn.findPath();
      algo_nn.twoOpt();
      std::vector<int> vec_path = algo_nn.getRoute();
      return vec_path;
    }
    return std::vector<int>();
}

PYBIND11_MODULE(py_graph_cpp, graph) {
  py::bind_vector<std::vector<int>>(graph, "VectorInt");
  graph.def("addVertex", &addVertex, "Add vertex to graph");
  graph.def("resetGraph", &resetGraph, "Remove all vertices from graph");
  graph.def("getNNRoute", &getNNRoute, "Get nearest neighbor route");
  graph.def("getTwoOptRoute", &getTwoOptRoute, "Get Two Opt route");
}
