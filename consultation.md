# Consultation Agenda - Kelly & Pruitt (2013) Replication

**Project**: Market Expectations in the Cross-Section of Present Values  
**Team**: Zara, Dylan

---

## Questions for Instructor

1. **Data period**: Paper uses ~1930-2011. Should we extend to present or match original sample?
2. **Book equity definition**: Multiple valid approaches exist (seq+txditc-ps vs ceq). Which is preferred?
3. **PLS implementation**: Use sklearn's PLSRegression or implement 3PRF from scratch?
4. **Table 1 scope**: Replicate full table (returns + dividend growth) or subset?

---

## Division of Responsibilities

### Zara
- Data pipeline setup (dodo.py, settings)
- `pull_CRSP_stock.py` - market returns, stock data
- Aggregate market returns + dividend growth calculation
- Chartbook site setup and GitHub Pages deployment

### Dylan
- `pull_CRSP_Compustat.py` - fundamentals data
- Book equity calculation and CRSP-Compustat merge
- Firm-level book-to-market ratio construction
- PLS / 3PRF implementation for factor extraction

### Joint
- Table 1 replication and validation
- Exploratory charts
- Final report review

---

## Feasibility Concerns

- CRSP CIZ format transition may cause discrepancies with original paper's SIZ-based sample
- Compustat coverage pre-1960 is limited; may affect early sample period
