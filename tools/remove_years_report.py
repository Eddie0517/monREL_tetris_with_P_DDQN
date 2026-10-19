# -*- coding: utf-8 -*-
with open('reports/EVALUATION_REPORT.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace entries in Table 2
text = text.replace("*(Demaine et al., 2002 [1])*", "*(Demaine et al. [1])*")
text = text.replace("*(Fahey, 2003 [6])*", "*(Fahey [6])*")
text = text.replace("*(Pierre Dellacherie, 2003 [6])*", "*(Pierre Dellacherie [6])*")
text = text.replace("**Stevens & Pradhan (2016)** [3]", "**Stevens & Pradhan** [3]")
text = text.replace("**Bertsekas & Tsitsiklis (1996)** [7]", "**Bertsekas & Tsitsiklis** [7]")
text = text.replace("**Lagoudakis et al. (2002)** [8]", "**Lagoudakis et al.** [8]")
text = text.replace("**de Farias & Van Roy (2006)** [9]", "**de Farias & Van Roy** [9]")
text = text.replace("**Ziao Chen (2021)** [5]", "**Ziao Chen** [5]")

# Replace in Section 3 Table
text = text.replace("Random Baseline (Demaine 2002)", "Random Baseline (Demaine)")
text = text.replace("Naive Greedy (Fahey 2003)", "Naive Greedy (Fahey)")
text = text.replace("Expert Heuristic (Dellacherie 2003)", "Expert Heuristic (Dellacherie)")

# Fix any glitch in math formula
text = text.replace(r"$(f_4 	imes 1.5)^2$", r"$(f_4 \times 1.5)^2$")

with open('reports/EVALUATION_REPORT.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated EVALUATION_REPORT.md successfully!")
