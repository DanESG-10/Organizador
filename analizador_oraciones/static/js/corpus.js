const CORPUS = [
  "casa la es grande",
  "estudiantes los estudian biblioteca en la",
  "juega niña la con pelota amarilla la",
  "libros los leen niños los",
  "la saqué basura yo",
  "una compró Julián computadora",
  "ganó rojo el carrera la coche",
  "puerta rebeldes la estudiantes dañaron los",
  "complejo resuelve problema un estudiante el",
  "caliente sopa hizo abuela mi",
  "reparó carpintero la mesa el",
  "por Luciano escrita fue carta la",
  "Carlos de casa la es",
  "caliente café el está",
  "pantalla viendo estamos nosotros la",
  "mensaje el recibió no coronel el",
  "domingos los abre no tienda la",
  "escuela la a fui no yo",
  "fotocopiadora la usar pueden ellos",
  "congreso el por aprobadas fueron leyes las",
  "caí me las de escaleras",
  "Radith hizo no tarea la",
  "se cayó escaleras las de",
  "ayudó Val con me tesis la",
  "joven juega tenis el",
];

// CORPUS
function obtenerEjemplosAleatorios(n = 4) {
  return [...CORPUS].sort(() => Math.random() - 0.5).slice(0, n);
}
