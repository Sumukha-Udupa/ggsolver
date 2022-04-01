#include "pybindings.h"
#include "../version.h"
#include "../types.h"
#include "../entity.h"
#include "../graph.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


using namespace ggsolver;
using namespace pybind11::literals;
namespace py = pybind11;


PYBIND11_MODULE(ggsolver, m) {

	// Public methods
	m.def("Version", &Version);

    // TValue
    py::enum_<TValue::Type>(m, "Type")
            .value("py_none", TValue::Type::py_none)
            .value("py_bool", TValue::Type::py_bool)
            .value("py_int", TValue::Type::py_int)
            .value("py_float", TValue::Type::py_float)
            .value("py_str", TValue::Type::py_str)
            .value("py_function", TValue::Type::py_function)
            .value("py_tuple", TValue::Type::py_tuple)
            .value("py_list", TValue::Type::py_list)
            .value("py_set", TValue::Type::py_set)
            .value("py_dict", TValue::Type::py_dict)
            .value("py_object", TValue::Type::py_object)
            .value("gg_entity", TValue::Type::gg_entity)
            .export_values();

    py::class_<TValue, std::shared_ptr<TValue>>(m, "TValue")
            .def(py::init<const bool&>())
            .def(py::init<const unsigned long&>())
            .def(py::init<const double&>())
            .def(py::init<const std::string&>())
            .def(py::init<const PEntity&>())
            .def(py::init<const std::vector<PValue>&>())
            .def(py::init<const std::unordered_set<PValue>&>())
            .def(py::init<const std::unordered_map<std::string, PValue>&>())
            .def(py::init<const py::handle&>())
            .def("set_object", &TValue::set_object)
            .def("set_entity", &TValue::set_entity)
            .def("get_type", &TValue::get_type)
            .def("get_object", &TValue::get_object)
            .def("get_entity", &TValue::get_entity<TEntity>)
            .def("get_function", &TValue::get_function<py::function>)
            ;

    // Attribute Map
//    py::class_<TEntity, std::shared_ptr<TEntity>>(m, "TEntity")
//            .def(py::init<>())
//            .def("is_special_attr", &TEntity::is_special_attr)
//            .def("has_attr", &TEntity::has_attr)
//            .def("get_attr_type", &TEntity::get_attr_type)
//            .def("get_attr", &TEntity::get_attr<json>)
//            .def("set_attr", &TEntity::set_attr<json>)
//            ;

    py::class_<TNode, std::shared_ptr<TNode>>(m, "TNode")
            .def(py::init<>())
            .def("is_special_attr", &TNode::is_special_attr)
            .def("has_attr", &TNode::has_attr)
            .def("get_attr_type", &TNode::get_attr_type)
            .def("get_attr", &TNode::get_attr<json>)
            .def("set_attr", &TNode::set_attr<json>)
            .def("get_node_id", &TNode::get_node_id)
            ;

    py::class_<TEdge, std::shared_ptr<TEdge>>(m, "TEdge")
            .def(py::init<>())
            .def("is_special_attr", &TEdge::is_special_attr)
            .def("has_attr", &TEdge::has_attr)
            .def("get_attr_type", &TEdge::get_attr_type)
            .def("get_attr", &TEdge::get_attr<json>)
            .def("set_attr", &TEdge::set_attr<json>)
            .def("get_edge_id", &TEdge::get_edge_id)
            .def("get_uid", &TEdge::get_uid)
            .def("get_vid", &TEdge::get_vid)
            ;

    py::class_<TGraph, std::shared_ptr<TGraph>>(m, "TGraph")
            .def(py::init<>())
            .def("add_node", py::overload_cast<>(&TGraph::add_node))
            .def("add_node", py::overload_cast<const json&>(&TGraph::add_node))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&, const json&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&, const json&>(&TGraph::add_edge))
            .def("add_nodes_from", py::overload_cast<const unsigned long&>(&TGraph::add_nodes_from))
            .def("add_nodes_from", py::overload_cast<const std::vector<json>&>(&TGraph::add_nodes_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::pair<unsigned long, unsigned long>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::pair<PNode, PNode>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<unsigned long, unsigned long, json>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<PNode, PNode, json>>>(&TGraph::add_edges_from))
            .def("rem_node", py::overload_cast<const unsigned long&>(&TGraph::rem_node))
            .def("rem_node", py::overload_cast<const PNode&>(&TGraph::rem_node))
            .def("rem_nodes_from", py::overload_cast<std::vector<unsigned long>>(&TGraph::rem_nodes_from))
            .def("rem_nodes_from", py::overload_cast<std::vector<PNode>>(&TGraph::rem_nodes_from))
            .def("rem_edge", py::overload_cast<const unsigned long&>(&TGraph::rem_edge))
            .def("rem_edge", py::overload_cast<const PEdge&>(&TGraph::rem_edge))
            .def("rem_edges_from", py::overload_cast<std::vector<unsigned long>>(&TGraph::rem_edges_from))
            .def("rem_edges_from", py::overload_cast<std::vector<PEdge>>(&TGraph::rem_edges_from))
            .def("has_node", py::overload_cast<const PNode&>(&TGraph::has_node))
            .def("has_node", py::overload_cast<const unsigned long&>(&TGraph::has_node))
            .def("has_edge", py::overload_cast<const unsigned long&>(&TGraph::has_edge))
            .def("has_edge", py::overload_cast<const PEdge&>(&TGraph::has_edge))
            .def("edges", &TGraph::edges)
            .def("in_edges", py::overload_cast<const unsigned long&>(&TGraph::in_edges))
            .def("in_edges", py::overload_cast<const PNode&>(&TGraph::in_edges))
            .def("out_edges", py::overload_cast<const unsigned long&>(&TGraph::out_edges))
            .def("out_edges", py::overload_cast<const PNode&>(&TGraph::out_edges))
            .def("successors", py::overload_cast<const unsigned long&>(&TGraph::successors))
            .def("successors", py::overload_cast<const PNode&>(&TGraph::successors))
            .def("predecessors", py::overload_cast<const unsigned long&>(&TGraph::predecessors))
            .def("predecessors", py::overload_cast<const PNode&>(&TGraph::predecessors))
            .def("number_of_nodes", &TGraph::number_of_nodes)
            .def("number_of_edges", &TGraph::number_of_edges)
            .def("size", &TGraph::size)
            .def("clear", &TGraph::clear)
            .def("reserve", &TGraph::reserve)
            .def("has_attr", &TGraph::has_attr)
            .def("get_attr_type", &TGraph::get_attr_type)
            .def("get_attr", &TGraph::get_attr<json>)
            .def("get_nodes_factory", &TGraph::get_nodes_factory)
            .def("get_edges_factory", &TGraph::get_edges_factory)
            .def("set_attr", &TGraph::set_attr<json>)
            ;

}
