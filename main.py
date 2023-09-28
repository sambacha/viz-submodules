#!/usr/bin/env python3

import os
import configparser
import pydot
import click


class Tree:
    def __init__(self, data=None):
        self.children = []
        self.data = data

    def create_child(self, tree):
        """Add a child to the current tree node."""
        assert isinstance(tree, Tree), "Expected 'tree' to be an instance of 'Tree'."
        self.children.append(tree)

    def get_children(self):
        """Return the children of the current tree node."""
        return self.children

    def get_child_by_url(self, url):
        """Recursively search for a child node with the given URL."""
        if self.data and self.data.get("url") == url:
            return self
        for child in self.children:
            result = child.get_child_by_url(url)
            if result:
                return result
        return None

    def get_data(self):
        """Return the data associated with the current tree node."""
        return self.data

    def display(self, indentation=0, with_url=False):
        """Recursively print the tree structure."""
        label = self._get_label(with_url)
        indent = indentation * "---"
        indent += " " if indent else ""
        print(indent + label)
        for child in self.children:
            child.display(indentation + 1, with_url)

    def build_graph(self, graph, parent, indentation, graph_mode, with_url):
        """Recursively build a pydot graph from the tree structure."""
        label = self._get_label(with_url, "\n")
        node_label = (
            f'"{str(indentation) + "-" + label}"'
            if graph_mode == "scattered"
            else f'"{label}"'
        )
        node = pydot.Node(node_label)
        indentation += 1
        if parent:
            graph.add_edge(pydot.Edge(parent, node))
        graph.add_node(node)
        for child in self.children:
            graph, indentation = child.build_graph(
                graph, node, indentation, graph_mode, with_url
            )
            indentation += 1
        return graph, indentation

    def _get_label(self, with_url, sep=" - "):
        """Retrieve the label for the current node, optionally including the URL."""
        label = (
            self.data["name"]
            if self.data and "name" in self.data and self.data["name"]
            else ""
        )
        if with_url and self.data and "url" in self.data and self.data["url"]:
            label += sep + self.data["url"]
        return label


def parse_git_module_file(file_path):
    """Parse a .gitmodules file and return a list of (path, URL) tuples."""
    assert os.path.exists(file_path), f"The file '{file_path}' does not exist."

    config = configparser.ConfigParser()
    config.read(file_path)
    modules = [
        (os.path.join(config[section]["path"]), config[section]["url"])
        for section in config.sections()
    ]
    return modules


def parse_repo(path, relpath=None, url=None):
    """Recursively parse a repository and its submodules into a tree structure."""
    assert os.path.exists(path), f"The path '{path}' does not exist."

    name = (
        os.path.normpath(os.path.relpath(path, start=relpath))
        if relpath
        else os.path.basename(os.path.normpath(path))
    )
    if not os.path.isfile(os.path.join(path, ".gitmodules")):
        return Tree({"name": name, "path": path, "url": url})

    tree = Tree({"name": name, "path": path, "url": url})
    module_file = os.path.join(path, ".gitmodules")
    if os.path.isfile(module_file):
        subs = parse_git_module_file(module_file)
        for p, u in subs:
            new_tree = parse_repo(os.path.join(path, p), relpath=relpath, url=u)
            tree.create_child(new_tree)
    return tree


@click.command()
@click.option(
    "-m",
    "--mode",
    default="text",
    show_default=True,
    help="Output Mode: text | png | xdot | dot",
)
@click.option(
    "-g",
    "--graph-mode",
    default="scattered",
    show_default=True,
    help="Graph Mode: scattered | clustered",
)
@click.option(
    "-o",
    "--out",
    default="graph",
    show_default=True,
    help="Output filename (without extension)",
)
@click.option(
    "-u",
    "--with-url",
    default=False,
    is_flag=True,
    show_default=True,
    help="Add repo URLs",
)
@click.option(
    "-r",
    "--relative-path",
    default=False,
    is_flag=True,
    show_default=True,
    help="Show relative path",
)
@click.argument("repo")
def main(mode, repo, graph_mode, out, with_url, relative_path):
    """Main function to parse a repo and display or save its structure."""
    assert mode in [
        "text",
        "png",
        "xdot",
        "dot",
    ], "Invalid mode. Choose among 'text', 'png', 'xdot', or 'dot'."
    assert graph_mode in [
        "scattered",
        "clustered",
    ], "Invalid graph mode. Expected 'scattered' or 'clustered'."

    tree = parse_repo(repo, relpath=repo) if relative_path else parse_repo(repo)
    if mode == "text":
        tree.display(with_url=with_url)
    else:
        graph = pydot.Dot(graph_type="digraph")
        graph, _ = tree.build_graph(graph, None, 1, graph_mode, with_url)
        if mode == "png":
            filename = out + ".png"
            graph.write_png(filename)
        elif mode == "xdot":
            filename = out + ".xdot"
            with open(filename, "w") as f:
                f.write(graph.to_string())
        elif mode == "dot":
            filename = out + ".dot"
            graph.write(filename, prog="dot", format="dot")


if __name__ == "__main__":
    main()
