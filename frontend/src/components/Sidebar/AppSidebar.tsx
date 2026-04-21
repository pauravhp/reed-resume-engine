import { BookOpen, LayoutDashboard, MessageSquare, User, Zap } from "lucide-react"

import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import { type Item, Main } from "./Main"
import { User as UserMenu } from "./User"
import useAuth from "@/hooks/useAuth"

const navItems: Item[] = [
  { icon: Zap,             title: "Generate",  path: "/generate"  },
  { icon: LayoutDashboard, title: "Dashboard", path: "/dashboard" },
  { icon: BookOpen,        title: "Banks",     path: "/banks"     },
  { icon: MessageSquare,   title: "Answers",   path: "/answers"   },
  { icon: User,            title: "Profile",   path: "/profile"   },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={navItems} />
      </SidebarContent>
      <SidebarFooter>
        <UserMenu user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
