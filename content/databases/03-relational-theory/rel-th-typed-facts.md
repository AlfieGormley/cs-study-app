---
id: rel-th-typed-facts
title: Relations as typed facts
level: basic
minutes: 4
sourceLesson: rel-th-relational-model
summary: Relations as typed facts, with explicit examples and the conditions that make the reasoning valid.
---

In 1970 Edgar F. Codd, a researcher at IBM, published *A Relational Model of Data for Large Shared Data Banks*. Many contemporary database interfaces were navigational: programs followed prescribed paths between records, coupling applications to access structures. Codd argued that applications should be insulated from representation changes.

Codd's idea was to describe data purely as **sets of facts**, with no pointers and no visible storage order. Programs say *what* they want, and the system works out *how* to fetch it. That separation, called **data independence**, is why you can add an index to a Postgres table today without touching a single query.

This lesson defines the vocabulary precisely. Every later lesson (algebra, dependencies, normal forms) builds on it.

## Relations, relational tuples and attributes

A **database relation** is a set of relational tuples that all share the same heading. Informally it is a table, but the precise definition matters.

```
Student
+-----+------+------+
| sid | name | year |   <- heading
+-----+------+------+
|  1  | Ada  |  2   |   <- relational tuple
|  2  | Ben  |  1   |
|  3  | Cat  |  2   |
+-----+------+------+
```

The drawing names the relation Student; its attributes are student id `sid`, student `name` and study `year`. This is the named-attribute presentation of the model: position in a printed table is a display choice. Codd’s original mathematical presentation used ordered domains; naming attributes avoids making that displayed order part of the meaning.

| Theory | SQL | Meaning |
|---|---|---|
| Relation | Table | A set of relational tuples |
| Tuple | Row | One fact |
| Attribute | Column | A named role |
| Domain | Type | Allowed values |

- The **relation heading** assigns each attribute name a domain. For example, `year` draws values from the integers one through four. A relational tuple assigns exactly one value from the correct domain to every attribute; a student name cannot occupy the year attribute.
- An **attribute domain** is the set of values an attribute may take. Codd required **atomic relational values**, indivisible from the database's point of view (more on that in the normal forms lesson).
- The **relation degree** (or arity) is the number of attributes: 3 above.
- The **cardinality** is the number of relational tuples: 3 above. It changes as rows are inserted; the degree does not.

### Each relational tuple is a true statement

The most useful way to read a relation is as a **relational predicate** with blanks:

> Student *sid* is called *name* and is in year *year*.

Every relational tuple fills in the blanks to make a true proposition. The relational tuple `(2, Ben, 1)` asserts "Student 2 is called Ben and is in year 1."

Under the **closed-world assumption**, the stored relation contains every true instance of its stated relational predicate. Only with that completeness assumption does an absent student relational tuple mean that the student does not exist in the population being modelled. SQL `NOT EXISTS` tests for returned rows regardless of whether the database is complete. A missing holiday booking can establish “no recorded holiday”; it cannot establish attendance, because illness and weekends are different facts.

```formula
r ⊆ D_sid × D_name × D_year
where
r: the finite set of Student relational tuples, shown in sid, name, year order for this card
D_sid: allowed student identifiers, here positive integers
D_name: allowed student names, here text strings
D_year: allowed study years, here integers one through four
⊆: is a subset of; every stored relational tuple must be a permitted combination
×: Cartesian product of domains, the set of all permitted value combinations
In words: The relation may contain only correctly typed combinations. Domains alone do not ensure that an identifier is unique; keys add that rule.
```

## Key takeaways

- A relational tuple assigns one correctly typed value to each named attribute.
- Degree counts attributes; cardinality counts relational tuples. Conclusions under the closed-world assumption require a complete relational predicate.

## Further reading

- [Codd: A Relational Model of Data (1970)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [Reiter: On Closed World Data Bases](https://www.cs.ubc.ca/sites/default/files/tr/1977/TR-77-16.pdf)
