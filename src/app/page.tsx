import { getAllContests } from "@/lib/contests";
import ActiveContestPage from "./ActiveContestPage";

export default function Home() {
  const contests = getAllContests();
  return <ActiveContestPage contests={contests} />;
}
