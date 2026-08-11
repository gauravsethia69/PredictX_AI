import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  discoverMachines,
  getReadableError,
  REFRESH_INTERVAL,
} from "../api/predictxApi";

const MachineContext = createContext(null);

const STORAGE_KEY = "predictx-selected-machine";

export function MachineProvider({ children }) {
  const [machines, setMachines] = useState([]);

  const [selectedMachineId, setSelectedMachineIdState] = useState(() => {
    return window.localStorage.getItem(STORAGE_KEY) || "";
  });

  const [loadingMachines, setLoadingMachines] = useState(true);
  const [machineError, setMachineError] = useState("");

  const refreshMachines = useCallback(async () => {
    try {
      const discovered = await discoverMachines(100);

      /*
       * Backend currently returns:
       *
       * ["MACHINE-001"]
       *
       * But the rest of the frontend expects:
       *
       * [{ machine_id: "MACHINE-001" }]
       *
       * Convert string machine IDs into the object format
       * without changing the backend/API contract.
       */
      const rawMachineList = Array.isArray(discovered)
        ? discovered
        : [];

      const machineList = rawMachineList.map((machine) => {
        if (typeof machine === "string") {
          return {
            machine_id: machine,
          };
        }

        return machine;
      });

      setMachines(machineList);
      setMachineError("");

      setSelectedMachineIdState((current) => {
        const stillExists = machineList.some(
          (machine) => machine.machine_id === current
        );

        if (stillExists) {
          return current;
        }

        const firstMachine =
          machineList[0]?.machine_id || "";

        if (firstMachine) {
          window.localStorage.setItem(
            STORAGE_KEY,
            firstMachine
          );
        } else {
          window.localStorage.removeItem(
            STORAGE_KEY
          );
        }

        return firstMachine;
      });
    } catch (error) {
      console.error(
        "Machine discovery failed:",
        error
      );

      setMachineError(
        getReadableError(error)
      );

      setMachines([]);
    } finally {
      setLoadingMachines(false);
    }
  }, []);

  useEffect(() => {
    refreshMachines();

    const timer = window.setInterval(
      refreshMachines,
      Math.max(
        REFRESH_INTERVAL * 4,
        10000
      )
    );

    return () => {
      window.clearInterval(timer);
    };
  }, [refreshMachines]);

  const setSelectedMachineId = useCallback(
    (machineId) => {
      setSelectedMachineIdState(machineId);

      if (machineId) {
        window.localStorage.setItem(
          STORAGE_KEY,
          machineId
        );
      } else {
        window.localStorage.removeItem(
          STORAGE_KEY
        );
      }
    },
    []
  );

  const selectedMachine = useMemo(() => {
    return (
      machines.find(
        (machine) =>
          machine.machine_id ===
          selectedMachineId
      ) || null
    );
  }, [
    machines,
    selectedMachineId,
  ]);

  const value = useMemo(
    () => ({
      machines,
      selectedMachine,
      selectedMachineId,
      setSelectedMachineId,
      refreshMachines,
      loadingMachines,
      machineError,
    }),
    [
      machines,
      selectedMachine,
      selectedMachineId,
      setSelectedMachineId,
      refreshMachines,
      loadingMachines,
      machineError,
    ]
  );

  return (
    <MachineContext.Provider value={value}>
      {children}
    </MachineContext.Provider>
  );
}

export function useMachine() {
  const context = useContext(MachineContext);

  if (!context) {
    throw new Error(
      "useMachine must be used inside MachineProvider."
    );
  }

  return context;
}