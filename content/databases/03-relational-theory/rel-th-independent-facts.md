---
id: rel-th-independent-facts
title: Independent facts, 4NF and 5NF
level: intermediate
minutes: 3
sourceLesson: rel-th-normal-forms
summary: Independent facts, 4NF and 5NF, with explicit examples and the conditions that make the reasoning valid.
---

## Beyond BCNF, briefly

BCNF removes redundancy caused by FDs, but not all redundancy. If an employee has a set of skills and, independently, a set of languages, storing `(emp, skill, language)` forces every skill to be paired with every language. That is a **multivalued dependency**: an employee determines a whole *set* of skills, independently of the other attributes.

```formula
emp ↠ skill
emp ↠ language
where
emp: the employee
skill: one of the employee's skills
language: one of the languages the employee speaks
↠: multivalued dependency (a double-headed arrow): the left side determines a set of values on the right, and that set does not depend on the remaining attributes
In words: an employee's skills and languages are two independent lists, so every combination ends up stored.
```

**4NF** splits it into `(emp, skill)` and `(emp, language)`. **5NF** handles join dependencies across three or more parts. Both are rare in practice, but the "independent facts in one table" smell is worth recognising.

## The exact condition matters

The dependency says more than “an employee can have several skills”. It requires all combinations of independently recorded skills and languages. Consider one employee with SQL and Python skills and English and French languages:

```
emp skill  language
 7  SQL    English
 7  SQL    French
 7  Python English
 7  Python French
```

There are four combinations. Recording only SQL/English and Python/French would say that the pairs are linked, not independent, and would violate the claimed multivalued dependency. Splitting the independent lists saves repetition while recovering those four rows by a natural join.

A multivalued dependency is trivial if its right attributes are already contained in the determinant, or the two sides together cover the whole heading. Fourth normal form requires a superkey determinant for every non-trivial multivalued dependency. Every FD implies an MVD, so this requirement also implies BCNF.

A **join dependency** says that a relation is always exactly the join of specified projections. Fifth normal form, also called project-join normal form, requires every non-trivial join dependency to follow from candidate-key rules. Three-way decompositions can matter even when no useful two-way split exists. Do not infer a join dependency merely because one sample happens to rejoin correctly: it must be a domain rule. Conversely, a supplier/part/project relation with no such rule must keep its three-way facts; splitting can invent combinations.

These are constraint-relative definitions. BCNF does not guarantee freedom from MVD redundancy, and 5NF does not promise that every application constraint or temporal fact is now represented correctly.

## Key takeaways

- Independent skill and language lists require all combinations in a combined table.
- 4NF controls non-trivial MVDs; 5NF controls join dependencies not implied by candidate keys.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
- [Fagin: Normal forms and relational database operators (1979)](https://research.ibm.com/publications/normal-forms-and-relational-database-operators)
- [Fagin: Domains and keys, section 5 definitions](https://s3.us.cloud-object-storage.appdomain.cloud/res-files/500-tods81.pdf)
