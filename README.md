<p align="center">
  <img src="/res/noesis.png" />
  
  Noesis plugin imports animation.
</p>


---

### Structure of *.aem*:

| char magic [7] or [9]    | AEMesh   | V2AEMesh | V3AEMesh | V4AEMesh | V5AEMesh |
| ------------------------ | -------- | -------- | -------- | -------- | -------- |
| **byte** *flags*               | ✔        | ✔        | ✔        | ✔        | ✔        |
| **ushort** *submesh_count* (sc) | ❌ just 1 | ❌ just 1 | ✔        | ✔        | ✔        |
*mesh* \[sc] 
| &emsp; **float** *pivot_point* \[3]               | ❌      | ❌        | ✔        | ✔        | ✔        |
| &emsp; **ushort** *face_indicies_count* (fc)           | ✔      | ✔        | ✔        | ✔        | ✔        |
| &emsp; **ushort** *face_indicies* \[fc/3]\[3]           | ✔***      | ✔        | ✔        | ✔        | ✔        |
| &emsp; **ushort** *triangle_strips_count* (tc)        | ✔ / ❌**      | ❌        | ❌        | ❌        | ❌        |
| &emsp; **ushort** *triangle_strips* \[tc]            | ✔ / ❌**      | ❌        | ❌        | ❌        | ❌        |
| &emsp; **ushort** *vertex_count* (vc)                  | ✔       | ✔        | ✔        | ✔        | ✔        |
| &emsp; **TYPE** *vertices* \[3\*vc]\[3]                      | ✔ **short** | ❌        | ❌        | ✔ **float** | ✔ **float** |
| &emsp; **short** *vertex_coord, sign* \[3\*vc]\[3]\[2] $(x, y, z)$, (<0&nbsp;or&nbsp;≥0) | ❌      | ✔        | ✔        | ❌        | ❌        |
| &emsp; **TYPE** *texture_coord* \[2\*vc]\[2] $(u, v)$                          | ✔ **short**, Q8* / Q12** | ✔ **short**, Q12* | ✔ **short**, Q12* | ✔ **float** | ✔ **float** |             
| &emsp; **TYPE** *normals* \[3\*vc]\[3] $(x, y, z)$                | ✔ **short**, Q8* / Q15** | ✔ **short**, Q15* | ✔ **short**, Q15* | ✔ **float** | ✔ **float** |
| &emsp; **TYPE** *material?* \[vc][2 or 4] $(g, b)/(a, r, g, b)?$           | ❌      | ❔ **short**   | ✔ **short**  | ✔ **float** | ✔ **float** |
| &emsp; **float** *bounding_sphere* \[4] $(x, y, z, r)$           | ❌      | ❌        | ❌        | ✔        | ✔        |
| &emsp; *animation data*                      | ❌      | ❌        | ✔/❔        | ✔        | ✔        |


\***Qn** is format of storing fixed point fractional numbers as integer in which **n** LSB (least significant bits) store fractional part, for example in Q8:\
    decimal: $24$, binary: $0001\,1000 \rightarrow \frac{24}{256} = 0.09375$, becouse $2^8=256$\
    decimal: $315$, binary: $1 \mathbf{.}0011\,1011 \rightarrow \frac{315}{256} = 1.23046875$\
    (in binary format dot $\mathbf{.}$ is just there for visual separation of integer and fractional parts)

\*\*There is rarer version of [V1]**AEMesh** similar to **V2** but without sign next to vertex coord. 

\*\*\*Common [V1]**AEmesh** can have indicies count not divisable by 3 becouse of triangle strip encoding used.

[V1]**AEmesh** has also a diffrent used in GOF3D for BREW. 
There can be more undocumented version.
### Animation data:

KeyFrame %d of %d\
Time: %d\
posx: %f\
posy: %f\
posz: %f\
rotx: %f\
roty: %f\
rotz: %f\
scax: %f\
scay: %f\
scaz: %f