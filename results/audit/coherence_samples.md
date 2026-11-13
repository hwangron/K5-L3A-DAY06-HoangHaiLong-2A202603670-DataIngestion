# Coherence samples (C uses the same chunks as B)

## P01 page 168 (section 2.3), char 876

### A `openstax-calc1-p168-fixed-01` (500 chars)

```text
e evaluated limits by looking at graphs or by constructing a table of values. In this section, we
establish laws for calculating limits and learn how to apply these laws. In the Student Project at the end of this section, you
have the opportunity to apply these limit laws to derive the formula for the area of a circle by adapting a method devised by
the Greek mathematician Archimedes. We begin by restating two useful limit results from the previous section. These two
results, together with the l
```

### B `openstax-calc1-p168-struct-00` (1011 chars)

```text
2.3 | The Limit Laws
Learning Objectives
2.3.1 Recognize the basic limit laws.
2.3.2 Use the limit laws to evaluate the limit of a function.
2.3.3 Evaluate the limit of a function by factoring.
2.3.4 Use the limit laws to evaluate the limit of a polynomial or rational function.
2.3.5 Evaluate the limit of a function by factoring or by using conjugates.
2.3.6 Evaluate the limit of a function by using the squeeze theorem.
In the previous section, we evaluated limits by looking at graphs or by constructing a table of values. In this section, we
establish laws for calculating limits and learn how to apply these laws. In the Student Project at the end of this section, you
have the opportunity to apply these limit laws to derive the formula for the area of a circle by adapting a method devised by
the Greek mathematician Archimedes. We begin by restating two useful limit results from the previous section. These two
results, together with the limit laws, serve as a foundation for calculating many limits.
```

## P02 page 173 (section 2.3), char 552

### A `openstax-calc1-p173-fixed-01` (500 chars)

```text
− 3)(2x + 1) = limx → 3 x2x + 1.
Step 3. Evaluate using the limit laws:
limx → 3 x2x + 1= 37.
Evaluate limx → −3x2 + 4x + 3x2 − 9 .
Example 2.18
Evaluating a Limit by Multiplying by a Conjugate
Evaluate limx → −1 x + 2− 1x + 1 .
Solution
Step 1. x + 2− 1x + 1 has the form0/0 at −1. Let’s begin by multiplying byx + 2+ 1, the conjugate of
x + 2− 1, on the numerator and denominator:
lim
x → −1
x + 2− 1
x + 1 = limx → −1 x + 2− 1x + 1 · x + 2+ 1x + 2+ 1.
Step 2. We then multiply out the numerator. W
```

### B `openstax-calc1-p173-struct-01` (313 chars)

```text
Step 2. For all x ≠ 3, x2 − 3x
2x2 − 5x − 3= x2x + 1. Therefore,
limx → 3 x(x − 3)(x − 3)(2x + 1) = limx → 3 x2x + 1.
Step 3. Evaluate using the limit laws:
limx → 3 x2x + 1= 37.
Evaluate limx → −3x2 + 4x + 3x2 − 9 .
Example 2.18
Evaluating a Limit by Multiplying by a Conjugate
Evaluate limx → −1 x + 2− 1x + 1 .
```

## P03 page 178 (section 2.3), char 613

### A `openstax-calc1-p178-fixed-01` (500 chars)

```text
im
x → 2−
x − 3x = − 12 and limx → 2− 1x − 2= −∞. Therefore, the product of(x − 3)/x and 1/(x − 2) has
a limit of +∞:
lim
x → 2−
x − 3
x2 − 2x = +∞.
Evaluate limx → 1 x + 2(x − 1)2.
The Squeeze Theorem
The techniques we have developed thus far work very well for algebraic functions, but we are still unable to evaluate limits
of very basic trigonometric functions. The next theorem, called thesqueeze theorem, proves very useful for establishing
basic trigonometric limits. This theorem allows us to
```

### B `openstax-calc1-p178-struct-00` (631 chars)

```text
left, the numerator approaches −1; and the denominator approaches 0. Consequently, the magnitude ofx − 3x(x − 2)
becomes infinite. To get a better idea of what the limit is, we need to factor the denominator:
lim
x → 2−
x − 3
x2 − 2x = limx → 2− x − 3x(x − 2).
Step 2. Since x − 2 is the only part of the denominator that is zero when 2 is substituted, we then separate
1/(x − 2) from the rest of the function:
= lim
x → 2−
x − 3x · 1x − 2.
Step 3. lim
x → 2−
x − 3x = − 12 and limx → 2− 1x − 2= −∞. Therefore, the product of(x − 3)/x and 1/(x − 2) has
a limit of +∞:
lim
x → 2−
x − 3
x2 − 2x = +∞.
Evaluate limx → 1 x + 2(x − 1)2.
```

## P04 page 183 (section 2.3), char 834

### A `openstax-calc1-p183-fixed-01` (500 chars)

```text
his idea to see what his geometric constructions could have
predicted about the limit.
We can estimate the area of a circle by computing the area of an inscribed regular polygon. Think of the regular
polygon as being made up ofn triangles. By taking the limit as the vertex angle of these triangles goes to zero, you can
obtain the area of the circle. To see this, carry out the following steps:
1. Express the height h and the base b of the isosceles triangle in Figure 2.31 in terms of θ and r.
Fig
```

### B `openstax-calc1-p183-struct-00` (946 chars)

```text
Deriving the Formula for the Area of a Circle
Some of the geometric formulas we take for granted today were first derived by methods that anticipate some of the
methods of calculus. The Greek mathematician Archimedes (ca. 287−212; BCE) was particularly inventive, using
polygons inscribed within circles to approximate the area of the circle as the number of sides of the polygon increased.
He never came up with the idea of a limit, but we can use this idea to see what his geometric constructions could have
predicted about the limit.
We can estimate the area of a circle by computing the area of an inscribed regular polygon. Think of the regular
polygon as being made up ofn triangles. By taking the limit as the vertex angle of these triangles goes to zero, you can
obtain the area of the circle. To see this, carry out the following steps:
1. Express the height h and the base b of the isosceles triangle in Figure 2.31 in terms of θ and r.
```

## P05 page 192 (section 2.4), char 869

### A `openstax-calc1-p192-fixed-01` (499 chars)

```text
ties, or jump
discontinuities. Intuitively, aremovable discontinuity is a discontinuity for which there is a hole in the graph, ajump
discontinuity is a noninfinite discontinuity for which the sections of the function do not meet up, and aninfinite
discontinuity is a discontinuity located at a vertical asymptote.Figure 2.37illustrates the differences in these types of
discontinuities. Although these terms provide a handy way of describing three common types of discontinuities, keep in
mind that
```

### B `openstax-calc1-p192-struct-01` (948 chars)

```text
Types of Discontinuities
As we have seen inExample 2.26 and Example 2.27, discontinuities take on several different appearances. We
classify the types of discontinuities we have seen thus far as removable discontinuities, infinite discontinuities, or jump
discontinuities. Intuitively, aremovable discontinuity is a discontinuity for which there is a hole in the graph, ajump
discontinuity is a noninfinite discontinuity for which the sections of the function do not meet up, and aninfinite
discontinuity is a discontinuity located at a vertical asymptote.Figure 2.37illustrates the differences in these types of
discontinuities. Although these terms provide a handy way of describing three common types of discontinuities, keep in
mind that not all discontinuities fit neatly into these categories.
Figure 2.37 Discontinuities are classified as (a) removable, (b) jump, or (c) infinite.
These three discontinuities are formally defined as follows:
```

## P06 page 197 (section 2.4), char 484

### A `openstax-calc1-p197-fixed-00` (500 chars)

```text
Figure 2.38 There is a number c ∈
a, b
that satisfies
f (c) = z.
Example 2.36
Application of the Intermediate Value Theorem
Show that f (x) = x − cosx has at least one zero.
Solution
Since f (x) = x − cosx is continuous over(−∞, +∞), it is continuous over any closed interval of the form
a, b
. If you can find an interval
a, b
suchthat f (a) and f (b) have opposite signs, you can use the
Intermediate Value Theorem to conclude there must be a real numberc in (a, b) that satisfies f (c) = 0. Note
t
```

### B `openstax-calc1-p197-struct-00` (734 chars)

```text
Figure 2.38 There is a number c ∈
a, b
that satisfies
f (c) = z.
Example 2.36
Application of the Intermediate Value Theorem
Show that f (x) = x − cosx has at least one zero.
Solution
Since f (x) = x − cosx is continuous over(−∞, +∞), it is continuous over any closed interval of the form
a, b
. If you can find an interval
a, b
suchthat f (a) and f (b) have opposite signs, you can use the
Intermediate Value Theorem to conclude there must be a real numberc in (a, b) that satisfies f (c) = 0. Note
that
f (0) = 0 − cos(0) = −1 < 0
and
fπ2 = π2 − cosπ2 = π2 > 0.
Using the Intermediate Value Theorem, we can see that there must be a real numberc in [0, π/2] that satisfies
f (c) = 0. Therefore, f (x) = x − cosx has at least one zero.
```

## P07 page 225 (section 3.1), char 502

### A `openstax-calc1-p225-fixed-01` (499 chars)

```text
ent line tof (x) at a to be the line passing through the point
a, f (a)
having
slope
(3.4)mtan = limh → 0f (a +h) − f (a)h
provided this limit exists.
Just as we have used two different expressions to define the slope of a secant line, we use two different forms to define the
slope of the tangent line. In this text we use both forms of the definition. As before, the choice of definition will depend
on the setting. Now that we have formally defined a tangent line to a function at a point, we can
```

### B `openstax-calc1-p225-struct-01` (823 chars)

```text
Definition
Let f (x) be a function defined in an open interval containinga. The tangent lineto f (x) at a is the line passing
through the point
a, f (a)
having slope
(3.3)mtan = limx → af (x) − f (a)x −a
provided this limit exists.
Equivalently, we may define the tangent line tof (x) at a to be the line passing through the point
a, f (a)
having
slope
(3.4)mtan = limh → 0f (a +h) − f (a)h
provided this limit exists.
Just as we have used two different expressions to define the slope of a secant line, we use two different forms to define the
slope of the tangent line. In this text we use both forms of the definition. As before, the choice of definition will depend
on the setting. Now that we have formally defined a tangent line to a function at a point, we can use this definition to find
equations of tangent lines.
```

## P08 page 231 (section 3.1), char 426

### A `openstax-calc1-p231-fixed-00` (499 chars)

```text
Figure 3.8 The slope of the secant line is the average velocity
over the interval [a, t]. The slope of the tangent line is the
instantaneous velocity.
We can useEquation 3.5to calculate the instantaneous velocity, or we can estimate the velocity of a moving object by
using a table of values. We can then confirm the estimate by using Equation 3.7.
Example 3.7
Estimating Velocity
A lead weight on a spring is oscillating up and down. Its position at timet with respect to a fixed horizontal
line is
```

### B `openstax-calc1-p231-struct-01` (346 chars)

```text
Example 3.7
Estimating Velocity
A lead weight on a spring is oscillating up and down. Its position at timet with respect to a fixed horizontal
line is given bys(t) = sint (Figure 3.9). Use a table of values to estimatev(0). Check the estimate by using
Equation 3.5.
Figure 3.9 A lead weight suspended from a spring in vertical
oscillatory motion.
```

## P09 page 240 (section 3.2), char 999

### A `openstax-calc1-p240-fixed-02` (500 chars)

```text
g section would quickly become quite tedious. In this section we define the derivative function and learn a
process for finding it.
Derivative Functions
The derivative function gives the derivative of a function at each point in the domain of the original function for which the
derivative is defined. We can formally define a derivative function as follows.
Definition
Let f be a function. Thederivative function, denoted byf ′, is the function whose domain consists of those values
of x such that t
```

### B `openstax-calc1-p240-struct-00` (1031 chars)

```text
3.2 | The Derivative as a Function
Learning Objectives
3.2.1 Define the derivative function of a given function.
3.2.2 Graph a derivative function from the graph of a given function.
3.2.3 State the connection between derivatives and continuity.
3.2.4 Describe three conditions for when a function does not have a derivative.
3.2.5 Explain the meaning of a higher-order derivative.
As we have seen, the derivative of a function at a given point gives us the rate of change or slope of the tangent line to the
function at that point. If we differentiate a position function at a given time, we obtain the velocity at that time. It seems
reasonable to conclude that knowing the derivative of the function at every point would produce valuable information about
the behavior of the function. However, the process of finding the derivative at even a handful of values using the techniques
of the preceding section would quickly become quite tedious. In this section we define the derivative function and learn a
process for finding it.
```

## P10 page 245 (section 3.2), char 732

### A `openstax-calc1-p245-fixed-01` (499 chars)

```text
f (x) − f (a)x −a .
We want to show that f (x) is continuous at a by showing that limx → af (x) = f (a). Thus,
limx → af (x) = limx → a
f (x) − f (a) + f (a)
= limx → af (x) − f (a)x −a · (x −a) + f (a) Multiply and divide f (x) − f (a) byx −a.
= limx → af (x) − f (a)x −a · limx → a(x −a) + limx → af (a)
= f ′(a) · 0 +f (a)
= f (a).
Therefore, since f (a) is defined and limx → af (x) = f (a), we conclude that f is continuous at a.
□
We have just proven that differentiability implies continuity,
```

### B `openstax-calc1-p245-struct-01` (1094 chars)

```text
Proof
If f (x) is differentiable at a, then f ′(a) exists and
f ′ (a) = limx → af (x) − f (a)x −a .
We want to show that f (x) is continuous at a by showing that limx → af (x) = f (a). Thus,
limx → af (x) = limx → a
f (x) − f (a) + f (a)
= limx → af (x) − f (a)x −a · (x −a) + f (a) Multiply and divide f (x) − f (a) byx −a.
= limx → af (x) − f (a)x −a · limx → a(x −a) + limx → af (a)
= f ′(a) · 0 +f (a)
= f (a).
Therefore, since f (a) is defined and limx → af (x) = f (a), we conclude that f is continuous at a.
□
We have just proven that differentiability implies continuity, but now we consider whether continuity implies
differentiability. To determine an answer to this question, we examine the functionf (x) = |x|. This function is continuous
everywhere; however, f ′(0) is undefined. This observation leads us to believe that continuity does not imply
differentiability. Let’s explore further. For f (x) = |x|,
f ′ (0) = limx → 0f (x) − f (0)x − 0 = limx → 0|x| − |0|x − 0 = limx → 0|x|x .
This limit does not exist because
lim
x → 0−
|x|x = −1 and limx → 0+ |x|x = 1.
See Figure 3.14.
```
