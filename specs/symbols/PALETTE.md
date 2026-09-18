# Symbol Palette — Program Specification v1.0.0

Every symbol in this document is a program specification unit.
Each unit declares: symbol, unicode, latex, family, arity, types, semantics, errors.

Nothing in this document is implemented. This is the specification.
The factory consumes specifications of this shape and emits code.

## Family A — Arithmetic

A1  +    U+002B  latex:+          arity:2  types:(number, number) -> number
    semantics: standard addition on the declared number type
    errors: TypeError on non-number input

A2  −    U+2212  latex:-          arity:2  types:(number, number) -> number
    semantics: standard subtraction
    errors: TypeError on non-number input

A3  ×    U+00D7  latex:\times      arity:2  types:(number, number) -> number
    semantics: multiplication; for matrices, matrix product
    errors: TypeError on incompatible shapes

A4  ÷    U+00F7  latex:\div        arity:2  types:(number, number≠0) -> number
    semantics: division
    errors: ZeroDivisionError, TypeError

A5  /    U+002F  latex:/          arity:2  types:(number, number≠0) -> number
    semantics: division in the host language
    errors: ZeroDivisionError, TypeError

A6  *    U+002A  latex:*          arity:2  types:(number, number) -> number
    semantics: multiplication; also unpacking in argument position
    errors: TypeError

A7  ^    U+005E  latex:\wedge      arity:2  types:(boolean, boolean) -> boolean
    semantics: logical AND in boolean domain
    errors: TypeError on non-boolean

A8  **   U+002A U+002A  latex:**  arity:2  types:(number, number) -> number
    semantics: exponentiation
    errors: TypeError, OverflowError

A9  %    U+0025  latex:\%         arity:2  types:(integer, integer≠0) -> integer
    semantics: modulo
    errors: ZeroDivisionError

A10 ±    U+00B1  latex:\pm        arity:1  types:(number) -> (number, number)
    semantics: yields both x+y and x−y where y is the second operand
    errors: TypeError

A11 ∓    U+2213  latex:\mp        arity:1  types:(number) -> (number, number)
    semantics: inverse of ±
    errors: TypeError

A12 √    U+221A  latex:\sqrt      arity:1  types:(number ≥ 0) -> number
    semantics: principal square root
    errors: ValueError on negative input

A13 ∛    U+221B  latex:\sqrt[3]   arity:1  types:(number) -> number
    semantics: principal cube root; defined for negatives
    errors: TypeError

A14 ∜    U+221C  latex:\sqrt[4]   arity:1  types:(number ≥ 0) -> number
    semantics: principal fourth root
    errors: ValueError on negative input

A15 !    U+0021  latex:!          arity:1  types:(non-negative integer) -> integer
    semantics: factorial
    errors: ValueError on negative

A16 !!   U+0021 U+0021  latex:!!  arity:1  types:(non-negative integer) -> integer
    semantics: double factorial
    errors: ValueError on negative

A17 |    U+007C  latex:|          arity:1  types:(number) -> number
    semantics: absolute value
    errors: TypeError

A18 |    U+007C  latex:|          arity:2  types:(integer, integer≠0) -> integer
    semantics: divisibility test; a|b iff b mod a == 0
    errors: ZeroDivisionError

A19 ⌊    U+230A  latex:\lfloor    arity:1  types:(number) -> integer
    semantics: floor

A20 ⌈    U+2308  latex:\lceil     arity:1  types:(number) -> integer
    semantics: ceiling

## Family B — Comparison

B1  =    U+003D  latex:=          arity:2  types:(T, T) -> boolean
    semantics: equality

B2  ≠    U+2260  latex:\neq        arity:2  types:(T, T) -> boolean
    semantics: inequality

B3  ≈    U+2248  latex:\approx     arity:2  types:(number, number [, tolerance]) -> boolean
    semantics: approximate equality within tolerance

B4  ≡    U+2261  latex:\equiv      arity:2  types:(T, T) -> boolean
    semantics: definitional equality / identity

B5  ≅    U+2245  latex:\cong       arity:2  types:(T, T) -> boolean
    semantics: isomorphism

B6  <    U+003C  latex:<          arity:2  types:(ordered T, ordered T) -> boolean
    semantics: strict less than

B7  >    U+003E  latex:>          arity:2  types:(ordered T, ordered T) -> boolean
    semantics: strict greater than

B8  ≤    U+2264  latex:\leq        arity:2  types:(ordered T, ordered T) -> boolean

B9  ≥    U+2265  latex:\geq        arity:2  types:(ordered T, ordered T) -> boolean

B10 ≪    U+226A  latex:\ll         arity:2  types:(ordered T, ordered T) -> boolean
    semantics: much less than

B11 ≫    U+226B  latex:\gg         arity:2  types:(ordered T, ordered T) -> boolean

B12 ∝    U+221D  latex:\propto     arity:2  types:(number, number) -> boolean
    semantics: proportionality

B13 ∼    U+223C  latex:\sim        arity:2  types:(T, T) -> boolean
    semantics: equivalence relation

B14 ≃    U+2243  latex:\simeq      arity:2  types:(T, T) -> boolean
    semantics: asymptotic equality

## Family C — Logic

C1  ¬    U+00AC  latex:\neg        arity:1  types:(boolean) -> boolean
    semantics: negation

C2  ∧    U+2227  latex:\wedge      arity:2  types:(boolean, boolean) -> boolean

C3  ∨    U+2228  latex:\vee        arity:2  types:(boolean, boolean) -> boolean

C4  ⊕    U+2295  latex:\oplus      arity:2  types:(boolean, boolean) -> boolean
    semantics: XOR in boolean domain; addition in GF(2)

C5  ⊻    U+22BB  latex:\veebar     arity:2  types:(boolean, boolean) -> boolean
    semantics: XOR

C6  →    U+2192  latex:\to         arity:2  types:(boolean, boolean) -> boolean
    semantics: implication

C7  ⇒    U+21D2  latex:\Rightarrow arity:2  types:(boolean, boolean) -> boolean

C8  ↔    U+2194  latex:\leftrightarrow arity:2  types:(boolean, boolean) -> boolean

C9  ⇔    U+21D4  latex:\Leftrightarrow arity:2  types:(boolean, boolean) -> boolean

C10 ⊤    U+22A4  latex:\top        arity:0  types: -> boolean
    semantics: true

C11 ⊥    U+22A5  latex:\bot        arity:0  types: -> boolean
    semantics: false

C12 ∀    U+2200  latex:\forall    arity:1  types:(domain, predicate) -> boolean

C13 ∃    U+2203  latex:\exists    arity:1  types:(domain, predicate) -> boolean

C14 ∄    U+2204  latex:\nexists   arity:1  types:(domain, predicate) -> boolean

C15 ∴    U+2234  latex:\therefore arity:1  types:(proof) -> claim

C16 ∵    U+2235  latex:\because   arity:1  types:(proof) -> claim

## Family D — Set theory

D1  ∈    U+2208  latex:\in         arity:2  types:(T, set[T]) -> boolean

D2  ∉    U+2209  latex:\notin      arity:2  types:(T, set[T]) -> boolean

D3  ∋    U+220B  latex:\ni         arity:2  types:(set[T], T) -> boolean

D4  ⊂    U+2282  latex:\subset     arity:2  types:(set[T], set[T]) -> boolean
    semantics: proper subset

D5  ⊃    U+2283  latex:\supset     arity:2  types:(set[T], set[T]) -> boolean

D6  ⊆    U+2286  latex:\subseteq   arity:2  types:(set[T], set[T]) -> boolean

D7  ⊇    U+2287  latex:\supseteq   arity:2  types:(set[T], set[T]) -> boolean

D8  ⊄    U+2284  latex:\nsubset    arity:2  types:(set[T], set[T]) -> boolean

D9  ⊅    U+2285  latex:\nsupset    arity:2  types:(set[T], set[T]) -> boolean

D10 ∪    U+222A  latex:\cup        arity:2  types:(set[T], set[T]) -> set[T]

D11 ∩    U+2229  latex:\cap        arity:2  types:(set[T], set[T]) -> set[T]

D12 ∖    U+2216  latex:\setminus  arity:2  types:(set[T], set[T]) -> set[T]

D13 ⊕    U+2295  latex:\oplus      arity:2  types:(set[T], set[T]) -> set[T]
    semantics: symmetric difference

D14 ⊖    U+2296  latex:\ominus     arity:2  types:(set[T], set[T]) -> set[T]

D15 ⊗    U+2297  latex:\otimes     arity:2  types:(set[T], set[T]) -> set[T]
    semantics: cartesian product

D16 ℘    U+2118  latex:\wp         arity:1  types:(set[T]) -> set[set[T]]
    semantics: power set

D17 ∅    U+2205  latex:\emptyset   arity:0  types: -> set[T]

## Family E — Discrete calculus and aggregation

E1  d    U+0064  latex:d          arity:1  types:(expression) -> expression
    semantics: derivative, symbolic

E2  ∂    U+2202  latex:\partial    arity:1  types:(expression, variable) -> expression
    semantics: partial derivative

E3  ∫    U+222B  latex:\int        arity:1  types:(expression, variable) -> expression
    semantics: indefinite integral

E4  ∬    U+222C  latex:\iint       arity:1  types:(expression, domain) -> expression

E5  ∭    U+222D  latex:\iiint      arity:1  types:(expression, domain) -> expression

E6  ∮    U+222E  latex:\oint       arity:1  types:(expression, closed path) -> expression

E7  ∇    U+2207  latex:\nabla      arity:1  types:(scalar field) -> vector field

E8  Δ    U+0394  latex:\Delta      arity:1  types:(value, value) -> number
    semantics: finite difference

E9  Σ    U+03A3  latex:\Sigma      arity:1  types:(iterable[number]) -> number
    semantics: sum over iterable

E10 Π    U+03A0  latex:\Pi         arity:1  types:(iterable[number]) -> number
    semantics: product over iterable

E11 ∏    U+220F  latex:\prod       arity:1  types:(iterable[number]) -> number

E12 ∐    U+2210  latex:\coprod     arity:1  types:(iterable[set[T]]) -> set[T]

E13 ⨁    U+2A01  latex:\bigoplus  arity:1  types:(iterable[additive]) -> additive

E14 ⨂    U+2A02  latex:\bigotimes arity:1  types:(iterable[multiplicative]) -> multiplicative

E15 ⨄    U+2A04  latex:\biguplus  arity:1  types:(iterable[set[T]]) -> set[T]

E16 lim  U+006C 0069 006D  latex:\lim  arity:2  types:(function, point) -> number
    semantics: limit

E17 sup  U+0073 0075 0070  latex:\sup  arity:1  types:(set[ordered]) -> value

E18 inf  U+0069 006E 0066  latex:\inf  arity:1  types:(set[ordered]) -> value

## Family F — Type-theoretic and category-theoretic operators

F1  ∘    U+2218  latex:\circ       arity:2  types:(function[B,C], function[A,B]) -> function[A,C]
    semantics: function composition

F2  ↦    U+21A6  latex:\mapsto     arity:2  types:(variable, expression) -> function

F3  ⇌    U+21CC  latex:\rightleftharpoons arity:2  types:(A, B) -> equilibrium

F4  ⇄    U+21C4  latex:\rightleftarrows arity:2  types:(A, B) -> reversible

F5  λ    U+03BB  latex:\lambda     arity:2  types:(parameters, body) -> function
    semantics: anonymous function

F6  μ    U+03BC  latex:\mu         arity:1  types:(function) -> fixed-point operator
    semantics: least fixed point

F7  ν    U+03BD  latex:\nu         arity:1  types:(function) -> cofixed-point operator
    semantics: greatest fixed point

F8  ⇒    U+21D2  latex:\Rightarrow arity:2  types:(A, B) -> function-type

F9  ⊣    U+22A3  latex:\dashv      arity:2  types:(F, G) -> adjunction with F ⊣ G

F10 ⊢    U+22A2  latex:\vdash      arity:2  types:(context, proposition) -> judgment

F11 ⊨    U+22A8  latex:\vDash      arity:2  types:(model, formula) -> boolean
    semantics: entailment

F12 □    U+25A1  latex:\Box        arity:1  types:(proposition) -> proposition
    semantics: necessarily

F13 ◇    U+25C7  latex:\Diamond    arity:1  types:(proposition) -> proposition
    semantics: possibly

F14 ○    U+25CB  latex:\circ       arity:1  types:(proposition) -> proposition
    semantics: next (temporal)

F15 U    U+0055  latex:\mathcal{U} arity:2  types:(proposition, proposition) -> proposition
    semantics: until (temporal)

F16 R    U+0052  latex:\mathcal{R} arity:2  types:(proposition, proposition) -> proposition
    semantics: release (temporal)

## Family G — Linear algebra and quantum notation

G1  ·    U+00B7  latex:\cdot       arity:2  types:(vector, vector) -> scalar

G2  ⊗    U+2297  latex:\otimes     arity:2  types:(space, space) -> product-space
    semantics: tensor product

G3  ⊙    U+2299  latex:\odot       arity:2  types:(vector, vector) -> vector
    semantics: element-wise product

G4  ⊕    U+2295  latex:\oplus      arity:2  types:(space, space) -> direct-sum
    semantics: direct sum

G5  ⟨    U+27E8  latex:\langle     arity:1  types: -> bra

G6  ⟩    U+27E9  latex:\rangle     arity:1  types: -> ket

G7  ‖    U+2016  latex:\|          arity:1  types:(vector) -> number
    semantics: norm

G8  †    U+2020  latex:\dagger     arity:1  types:(operator) -> operator
    semantics: hermitian conjugate

G9  −1   U+207B U+00B9  latex:^{-1} arity:1  types:(operator) -> operator
    semantics: inverse

## Family H — Programming operators

H1  =    assignment
H2  +=   U+002B U+003D  compound assignment addition
H3  -=   U+002D U+003D  compound assignment subtraction
H4  *=   U+002A U+003D  compound assignment multiplication
H5  /=   U+002F U+003D  compound assignment division
H6  %=   U+0025 U+003D  compound assignment modulo
H7  ==   equality test
H8  !=   inequality test
H9  ===  strict equality test
H10 < > <= >=  comparison
H11 && || !    boolean operators
H12 & | ^ ~    bitwise operators
H13 << >>      shifts
H14 >>>        unsigned right shift
H15 ?:         ternary
H16 ->         arrow
H17 =>         fat arrow
H18 ::         scope resolution
H19 |>         pipe forward
H20 <|         pipe backward
H21 >> <<      bind operators (monadic)
H22 >>=        monadic bind
H23 <=<        kleisli composition

## Family I — Physics notation

I1  Ĥ    hatted hamiltonian
I2  L̂    hatted lagrangian
I3  p̂    momentum operator
I4  x̂    position operator
I5  ∠    angle
I6  ⟂    perpendicular
I7  ∥    parallel

## Counts

Family A: 20
Family B: 14
Family C: 16
Family D: 17
Family E: 18
Family F: 16
Family G: 9
Family H: 23
Family I: 7
Total: 140 symbols specified.
