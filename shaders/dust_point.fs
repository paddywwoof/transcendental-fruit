precision mediump float;

uniform vec3 unib[4];
// see docstring Buffer
uniform vec3 unif[20];

varying float dist;

void main(void) {
  vec4 texc = vec4(unib[1], 1.0); // ------ basic colour from material vector
  if (texc.a < unib[0][2]) discard; // ------ to allow rendering behind the transparent parts of this object
  float ffact = smoothstep(unif[5][0]/3.0, unif[5][0], dist); // ------ smoothly increase fog between 1/3 and full fogdist

  //if (distance(gl_PointCoord, vec2(0.5)) > 0.5) discard; //circular points
  gl_FragColor = (1.0 - ffact) * texc + ffact * vec4(unif[4], unif[5][1]); // ------ combine using factors
  gl_FragColor.rgb *= clamp(fract(vec3(0.15, 0.27, 0.05) * dist), 0.25, 1.0);
  vec2 alpha = abs(gl_PointCoord - vec2(0.5));
  gl_FragColor.a *= unif[5][2] * (1.0 - smoothstep(0.0, 0.5, alpha[0] + alpha[1]));
}


