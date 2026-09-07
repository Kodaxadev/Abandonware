(() => {
  const upstreamDos = window.Dos;
  if (typeof upstreamDos !== "function") {
    throw new Error("Pinned js-dos runtime did not initialize before bridge.js");
  }

  const LOCAL_EMULATOR_PATH = "runtime/jsdos/emulators/";

  window.Dos = (element, options = {}) => upstreamDos(element, {
    ...options,
    pathPrefix: LOCAL_EMULATOR_PATH
  });

  window.ABANDONWARE_JSDOS = Object.freeze({
    version: "8.4.1",
    pathPrefix: LOCAL_EMULATOR_PATH,
    provenance: "runtime/jsdos/PROVENANCE.json"
  });
})();
