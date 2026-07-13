
class Document:
    def __init__(self):
        self.contents = []
        self.definitions = []
        self.packages = ["hyperref", "xcolor"]

    def add(self, type, content):
        match type:
            case "table":
                self.contents.append(
                    Table(content)
                )
                return

            case _:
                raise ValueError(f"Unknown type: {type}")


    def render(self):
        return f"""\documentclass{{article}}
        \\title{{Commit Report}}
        \\date{{\\today}}

        {"".join([f"\\usepackage{{{package}}}\n" for package in self.packages])}


        {"".join([definition.render() for definition in self.definitions])}

        \\begin{{document}}

        \\maketitle
        \\newpage

        {"".join([content.render() for content in self.contents])}

        \\end{{document}}
        """.replace("[", "{").replace("]", "}")
    
            



class Table:
    def __init__(self, content):
        self.content = content

    def render(self):
        return f"""\\begin{{table}}[]
        \\centering
        \\vline
        \\begin{{tabular}}{{c|c|c|c|c|c|c}}
            {self.content}
        \\end{{tabular}}
        \\end{{table}}
        """