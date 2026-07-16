
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



"""
new latex format
```
\documentclass[11pt,a4paper]{article}
\usepackage{everypage}
\usepackage[margin=1in]{geometry}
\usepackage[table]{xcolor}
\usepackage{tikz}
\usepackage{tabularx}
\usepackage{tcolorbox}
\usepackage{fancyhdr}
\usepackage{amssymb} 
\usepackage{hyperref}

% Fix font warnings: Import 'lmodern' to allow arbitrary large font scaling
\usepackage{lmodern}

% --- Brand Colors from Figma ---
\definecolor{purp}{HTML}{310062}
\definecolor{lightgrey}{HTML}{F5F5F5}
\definecolor{darkgrey}{HTML}{333333}
\definecolor{insertion}{HTML}{2EA043}
\definecolor{deletion}{HTML}{D73A49}
\definecolor{verified}{HTML}{0066FF}

% Set default text color globally
\color{darkgrey}

\tcbset{
    frame empty,
    colback=lightgrey,
    arc=3px,
    boxrule=0pt,
    left=10pt, right=10pt, top=10pt, bottom=10pt
}


\newcommand{\drawcorners}{%
  \begin{tikzpicture}[remember picture, overlay]
    % Top Right Corner Design (Hollow L-Shape)
    \fill[purp] ([xshift=-4.5cm]current page.north east) -- 
                ([xshift=-3.9cm, yshift=-0.6cm]current page.north east) -- 
                ([xshift=-0.6cm, yshift=-0.6cm]current page.north east) -- 
                ([xshift=-0.6cm, yshift=-3.9cm]current page.north east) -- 
                ([yshift=-4.5cm]current page.north east) -- 
                (current page.north east) -- cycle;

    % Bottom Left Corner Design (Hollow L-Shape)
    \fill[purp] ([yshift=4.5cm]current page.south west) -- 
                ([yshift=3.9cm, xshift=0.6cm]current page.south west) -- 
                ([xshift=0.6cm, yshift=0.6cm]current page.south west) -- 
                ([xshift=3.9cm, yshift=0.6cm]current page.south west) -- 
                ([xshift=4.5cm]current page.south west) -- 
                (current page.south west) -- cycle;
  \end{tikzpicture}%
}


\AddEverypageHook{\drawcorners}

% Document Font Styling (Uses Sans-Serif)
\renewcommand{\familydefault}{\sfdefault}

\pagestyle{fancy}
\fancyhf{} 
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\thepage} 

\begin{document}

% ================= PAGE 1: COVER =================
\thispagestyle{empty} 
\begin{center}
    \vspace*{6cm}
    {\fontsize{38}{44}\selectfont \bfseries \color{purp} PROJECT} \\[0.2cm]
    {\fontsize{38}{44}\selectfont \bfseries \color{purp} REPORT} \\[0.6cm]
    {\fontsize{18}{22}\selectfont \bfseries \today}
\end{center}
\clearpage

% ================= PAGE 2: SUMMARY =================
\section*{{\fontsize{32}{36}\selectfont \bfseries \color{purp} SUMMARY}}
\vspace{-0.3cm}
{\large \bfseries 9 commits, 3 collaborators}

\vspace{1.5cm}

\subsection*{{\fontsize{20}{24}\selectfont \color{black} New Releases}}
\vspace{-0.2cm}
{\small 1 new release.}

\vspace{0.2cm}
% Styled Table 1: New Releases
\renewcommand{\arraystretch}{1.3}
\rowcolors{2}{lightgrey}{white}
\noindent
\begin{tabularx}{\textwidth}{l X l r}
    \rowcolor{lightgrey!70}
    \textbf{\# id} & \textbf{Title} & \textbf{\# commit id} & \textbf{Verified} \\
    v19.2.7 & Release 19.2.7 (June 1st, 2026) & 6117d7cca4906492c51f... & \color{verified}{\checkmark \scriptsize Verified} \\
    v19.2.7 & Release 19.2.7 (June 1st, 2026) & 6117d7cca4906492c51f... & \color{verified}{\checkmark \scriptsize Verified} \\
    v19.2.7 & Release 19.2.7 (June 1st, 2026) & 6117d7cca4906492c51f... & \color{verified}{\checkmark \scriptsize Verified} \\
    v19.2.7 & Release 19.2.7 (June 1st, 2026) & 6117d7cca4906492c51f... & \color{verified}{\checkmark \scriptsize Verified} \\
    v19.2.7 & Release 19.2.7 (June 1st, 2026) & 6117d7cca4906492c51f... & \color{verified}{\checkmark \scriptsize Verified} \\
\end{tabularx}

\vspace{1cm}

\subsection*{{\fontsize{20}{24}\selectfont \color{black} Recent Commits}}
\vspace{-0.2cm}
{\small 4 recent commits}

\vspace{0.2cm}
% Styled Table 2: Recent Commits
\rowcolors{2}{lightgrey}{white}
\noindent
\begin{tabularx}{\textwidth}{l X l l r}
    \rowcolor{lightgrey!70}
    \textbf{\# id} & \textbf{Title} & \textbf{Author} & \textbf{Date} & \textbf{\# changes} \\
    7023f... & [DevTools] Don't reconnect p... & \underline{Saransh-Jainbu} & 2026-07-14 & \color{insertion}{+12}~\color{deletion}{-1} \\
    7023f... & [DevTools] Don't reconnect p... & \underline{Saransh-Jainbu} & 2026-07-14 & \color{insertion}{+12}~\color{deletion}{-1} \\
    7023f... & [DevTools] Don't reconnect p... & \underline{Saransh-Jainbu} & 2026-07-14 & \color{insertion}{+12}~\color{deletion}{-1} \\
    7023f... & [DevTools] Don't reconnect p... & \underline{Saransh-Jainbu} & 2026-07-14 & \color{insertion}{+12}~\color{deletion}{-1} \\
\end{tabularx}
\clearpage

% ================= PAGE 3: DETAILS =================
\newtcolorbox{commitbox}{
    frame empty,
    colback=white,
    boxrule=0pt,
    arc=0pt,
    left=0pt, right=0pt, top=0pt, bottom=0pt
}
 
 
\section*{{\fontsize{32}{36}\selectfont \bfseries \color{purp} DETAILS}}
\vspace{-0.3cm}
{\large \bfseries Commits on this page: 7023f2b, 9e8d7c6, f4e3d2c}
 
\vspace{0.5cm}
 
% Set a tight baseline stretch for the metadata row
\renewcommand{\arraystretch}{1.1}
\setlength{\tabcolsep}{8pt}
\arrayrulecolor{black!60}
 
% Commit Card 1
\begin{commitbox}
\noindent
\begin{tabularx}{\textwidth}{|>{\hsize=1.2\hsize}X|>{\hsize=1.0\hsize}X|>{\hsize=1.4\hsize}X|>{\hsize=0.7\hsize\raggedleft\arraybackslash}X|>{\hsize=0.7\hsize\raggedleft\arraybackslash}X|}
\hline
% Added vertical struts \rule{top}{bottom} to keep this row spacious
\multicolumn{5}{|l|}{\rule{0pt}{0.5cm}\color{purp}\textbf{\large Commit: [DevTools] Don't reconnect parser on every reload}\rule[-0.25cm]{0pt}{0.25cm}} \\
\hline
\multicolumn{3}{|l|}{\rule{0pt}{0.4cm}\color{purp}7023f2b} & \multicolumn{2}{r|}{13 lines changed\rule[-0.2cm]{0pt}{0.25cm}} \\
\hline
\color{purp}main & \color{purp}a1b2c3d & \color{purp}Saransh-Jainbu & \color{insertion}{\textbf{+12}} & \color{deletion}{\textbf{-1}} \\
\hline
\multicolumn{5}{|p{\dimexpr\textwidth-2\tabcolsep-6\arrayrulewidth\relax}|}{\rule{0pt}{0.4cm}Fixed an performance issue where the bridge parser would aggressively reset active connections during hot module replacement. Background tabs now retain persistent state successfully.\rule[-1.2cm]{0pt}{1.2cm}} \\
\hline
\end{tabularx}
\end{commitbox}
 
\vspace{0.4cm}
 
% Commit Card 2
\begin{commitbox}
\noindent
\begin{tabularx}{\textwidth}{|>{\hsize=1.2\hsize}X|>{\hsize=1.0\hsize}X|>{\hsize=1.4\hsize}X|>{\hsize=0.7\hsize\raggedleft\arraybackslash}X|>{\hsize=0.7\hsize\raggedleft\arraybackslash}X|}
\hline
\multicolumn{5}{|l|}{\rule{0pt}{0.5cm}\color{purp}\textbf{\large Commit: feat: Add nested workspace theme context merging}\rule[-0.25cm]{0pt}{0.25cm}} \\
\hline
\multicolumn{3}{|l|}{\rule{0pt}{0.4cm}\color{purp}9e8d7c6} & \multicolumn{2}{r|}{142 lines changed\rule[-0.2cm]{0pt}{0.25cm}} \\
\hline
\color{purp}feature/themes & \color{purp}7023f2b & \color{purp}jsmith\_dev & \color{insertion}{\textbf{+118}} & \color{deletion}{\textbf{-24}} \\
\hline
\multicolumn{5}{|p{\dimexpr\textwidth-2\tabcolsep-6\arrayrulewidth\relax}|}{\rule{0pt}{0.4cm}Introduced multi-level context inheritance for user color variables. Inner components now correctly merge and override standard layout configurations with custom themes without memory bloat.\rule[-1.2cm]{0pt}{1.2cm}} \\
\hline
\end{tabularx}
\end{commitbox}
 
\vspace{0.4cm}
 
% Commit Card 3
\begin{commitbox}
\noindent
\begin{tabularx}{\textwidth}{|>{\hsize=1.2\hsize}X|>{\hsize=1.0\hsize}X|>{\hsize=1.4\hsize}X|>{\hsize=0.7\hsize\raggedleft\arraybackslash}X|>{\hsize=0.7\hsize\raggedleft\arraybackslash}X|}
\hline
\multicolumn{5}{|l|}{\rule{0pt}{0.5cm}\color{purp}\textbf{\large Commit: fix(core): Prevent memory leak in hook listener registries}\rule[-0.25cm]{0pt}{0.25cm}} \\
\hline
\multicolumn{3}{|l|}{\rule{0pt}{0.4cm}\color{purp}f4e3d2c} & \multicolumn{2}{r|}{8 lines changed\rule[-0.2cm]{0pt}{0.25cm}} \\
\hline
\color{purp}hotfix/leak & \color{purp}9e8d7c6 & \color{purp}eng\_lead & \color{insertion}{\textbf{+6}} & \color{deletion}{\textbf{-2}} \\
\hline
\multicolumn{5}{|p{\dimexpr\textwidth-2\tabcolsep-6\arrayrulewidth\relax}|}{\rule{0pt}{0.4cm}Properly cleaned up internal event emitters in the cleanup hook callback. This prevents global instances from retaining references to destroyed DOM elements on window resize cycles.\rule[-1.2cm]{0pt}{1.2cm}} \\
\hline
\end{tabularx}
\end{commitbox}
 

\end{document}
```

"""